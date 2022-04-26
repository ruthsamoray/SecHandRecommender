import pandas as pd
import numpy as np
import math
import pickle

ITEMS_NUM = 60
SIMILARITY_MATRIX_PATH = 'w_matrix.pkl'


class RecommenderBaseModel:
	"""
	Implements the ML model for the recommender
	"""
	def __init__(self, data_filename, load_existing_sim_matrix):
		self.ratings = pd.read_csv(data_filename, encoding='"ISO-8859-1"')
		self.process_ratings_data()
		self.init_similarity_matrix(load_existing_sim_matrix)

		self.items = list(range(1, ITEMS_NUM+1))
		self.users = dict()
		self.cur_user = ""

	def process_ratings_data(self):
		"""
		process all the current ratings data to recommend to the user
		"""
		self.rating_mean = self.ratings.groupby(['itemId'], as_index = False, sort = False).mean().rename(columns = {'rating': 'rating_mean'})[['itemId','rating_mean']]
		self.adjusted_ratings = pd.merge(self.ratings,self.rating_mean,on = 'itemId', how = 'left', sort = False)
		self.adjusted_ratings['rating_adjusted'] = self.adjusted_ratings['rating']-self.adjusted_ratings['rating_mean']
		# replace 0 adjusted rating values to 1*e-8 in order to avoid 0 denominator
		self.adjusted_ratings.loc[self.adjusted_ratings['rating_adjusted'] == 0, 'rating_adjusted'] = 1e-8

	def init_similarity_matrix(self, load_existing_sim_matrix):
		"""
		initialize and save in the model the matrix of the similarities between each two items.
		:param load_existing_sim_matrix: if True, load an existing matrix. if False, calculates it.
		"""
		# define weight matrix
		self.similarity_matrix = pd.DataFrame(columns=['item_1', 'item_2', 'weight'])
		# load weight matrix from pickle file
		if load_existing_sim_matrix:
			with open(SIMILARITY_MATRIX_PATH, 'rb') as input:
				self.similarity_matrix = pickle.load(input)
			input.close()
		# calculate the similarity values
		else:
			self.build_similarity_matrix()

	def build_similarity_matrix(self):
		"""
		if the similarity matrix wasn't loaded, builds it based on the current ratings.
		"""
		distinct_items = np.unique(self.adjusted_ratings['itemId'])
		i = 0
		# for each item_1 in all items
		for item_1 in distinct_items:
			# extract all users who rated item_1
			user_data = self.adjusted_ratings[self.adjusted_ratings['itemId'] == item_1]
			distinct_users = np.unique(user_data['userId'])

			# record the ratings for users who rated both item_1 and item_2
			record_row_columns = ['userId', 'item_1', 'item_2', 'rating_adjusted_1', 'rating_adjusted_2']
			record_item_1_2 = pd.DataFrame(columns=record_row_columns)
			# for each customer C who rated item_1
			for c_userid in distinct_users:
				# the customer's rating for item_1
				c_item_1_rating = user_data[user_data['userId'] == c_userid]['rating_adjusted'].iloc[0]
				# extract items rated by the customer excluding item_1
				c_user_data = self.adjusted_ratings[(self.adjusted_ratings['userId'] == c_userid) & (self.adjusted_ratings['itemId'] != item_1)]
				c_distinct_items = np.unique(c_user_data['itemId'])

				# for each item rated by customer C as item=2
				for item_2 in c_distinct_items:
					# the customer's rating for item_2
					c_item_2_rating = c_user_data[c_user_data['itemId'] == item_2]['rating_adjusted'].iloc[0]
					record_row = pd.Series([c_userid, item_1, item_2, c_item_1_rating, c_item_2_rating], index=record_row_columns)
					record_item_1_2 = record_item_1_2.append(record_row, ignore_index=True)

			# calculate the similarity values between item_1 and the above recorded items
			distinct_item_2 = np.unique(record_item_1_2['item_2'])
			# for each item 2
			for item_2 in distinct_item_2:
				paired_item_1_2 = record_item_1_2[record_item_1_2['item_2'] == item_2]
				sim_value_numerator = (paired_item_1_2['rating_adjusted_1'] * paired_item_1_2['rating_adjusted_2']).sum()
				sim_value_denominator = np.sqrt(np.square(paired_item_1_2['rating_adjusted_1']).sum())\
										* np.sqrt(np.square(paired_item_1_2['rating_adjusted_2']).sum())
				sim_value_denominator = sim_value_denominator if sim_value_denominator != 0 else 1e-8
				sim_value = sim_value_numerator / sim_value_denominator
				self.similarity_matrix = self.similarity_matrix.append(pd.Series([item_1, item_2, sim_value],
																				 index=['item_1', 'item_2', 'weight']),
																	   ignore_index=True)

			i = i + 1

		# output weight matrix to pickle file
		with open(SIMILARITY_MATRIX_PATH, 'wb') as output:
			pickle.dump(self.similarity_matrix, output, pickle.HIGHEST_PROTOCOL)
		output.close()

	def login_user(self, username):
		"""
		login the given user.
		:param username: username to load as current user
		"""
		if username not in self.users:
			self.users[username] = self.items.copy()
		self.cur_user = username

	def get_recommendations(self, num_of_recommendations):
		"""
		get the recommendations of the current user based on the current collected data
		:param num_of_recommendations: number of items to recommend
		:return: list of items indexes
		"""
		distinct_items = np.unique(self.adjusted_ratings['itemId'])
		user_ratings_all_items = pd.DataFrame(columns=['itemId', 'rating'])
		user_ratings = self.adjusted_ratings[self.adjusted_ratings['userId'] == self.cur_user]

		# calculate the ratings for all items that the user hasn't rated
		i = 0
		for item in distinct_items:
			user_rating = user_ratings[user_ratings['itemId'] == item]
			if user_rating.shape[0] > 0:
				rating_value = user_ratings_all_items.loc[i, 'rating'] = user_rating["rating"].iloc[0]
			else:
				rating_value = user_ratings_all_items.loc[i, 'rating'] = self.predict(item)
			user_ratings_all_items.loc[i] = [item, rating_value]
			i = i + 1

		# select top num_of_recommendations items rated by the user
		recommendations = user_ratings_all_items.sort_values(by=['rating'], ascending=False).head(num_of_recommendations)
		return [int(item[1:]) for item in recommendations["itemId"]]

	def predict(self, item):
		"""
		predict the rating of the given item for the current user.
		:param item: the itemId to predict rating for
		:return: the predicted rating
		"""
		mean_rating = self.rating_mean[self.rating_mean['itemId'] == item]['rating_mean'].iloc[0]
		# calculate the rating of the given item by the given user
		user_other_ratings = self.adjusted_ratings[self.adjusted_ratings['userId'] == self.cur_user]
		user_distinct_items = np.unique(user_other_ratings['itemId'])
		sum_weighted_other_ratings = 0
		sum_weights = 0
		for item_j in user_distinct_items:
			#if rating_mean[rating_mean['itemId'] == item_j].shape[0] > 0:
			rating_mean_j = self.rating_mean[self.rating_mean['itemId'] == item_j]['rating_mean'].iloc[0]
			# only calculate the weighted values when the weight between item_1 and item_2 exists in weight matrix
			w_item_1_2 = self.similarity_matrix[(self.similarity_matrix['item_1'] == item) &
												(self.similarity_matrix['item_2'] == item_j)]
			if w_item_1_2.shape[0] > 0:
				user_rating_j = user_other_ratings[user_other_ratings['itemId']==item_j]
				sum_weighted_other_ratings += (user_rating_j['rating'].iloc[0] - rating_mean_j) * w_item_1_2['weight'].iloc[0]
				sum_weights += np.abs(w_item_1_2['weight'].iloc[0])

		# if sum_weights is 0 (which may be because of no ratings from new users), use the mean ratings
		return mean_rating if sum_weights == 0 else mean_rating + sum_weighted_other_ratings/sum_weights

	def update_ratings(self, items, ratings):
		"""
		update the model's ratings data according to the given ratings, that the current user rated.
		:param items: the items the current user rated
		:param ratings: the ratings of the given items
		"""
		user_id = [self.cur_user for i in range(len(items))]
		self.ratings = pd.concat([self.ratings,
								  pd.DataFrame(data={"userId": user_id, "itemId": items, "rating": ratings})],
								 ignore_index=True).astype({"rating": np.int64})
		self.process_ratings_data()

	def get_item_for_rating(self):
		"""
		get a random item that the current user hasn't rated yet. if user rated all items,
		it will choose randomly again from all rated items.
		:return: index of the item to rate
		"""
		if self.cur_user == "":
			return self.items[np.random.randint(0, len(self.items))]
		if len(self.users[self.cur_user]) == 0:
			self.users[self.cur_user] = self.items.copy()
		random_index = np.random.randint(0, len(self.users[self.cur_user]))
		return self.users[self.cur_user].pop(random_index)