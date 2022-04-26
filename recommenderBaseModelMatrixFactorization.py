import pandas as pd
import numpy as np
from matrix_factorization import KernelMF

ITEMS_NUM = 60

class RecommenderBaseModel:
	def __init__(self, data_filename):
		self.users = dict()
		self.items = list(range(1, ITEMS_NUM+1))
		self.cur_user = ""
		self.process_initial_data(data_filename)
		self.cur_recommendation = []
		self.users_data_for_update = pd.DataFrame(columns=["user_id", "item_id", "rating"])

	def process_initial_data(self, data_filename):
		"""
		process all initial data from the given file, and train the model
		:param data_filename:
		"""
		self.initial_data = pd.read_csv(data_filename, names=["user_id", "item_id", "rating"], sep=",", engine="python")
		self.users_data, self.ratings = (self.initial_data[["user_id", "item_id"]], self.initial_data["rating"],)
		self.matrix_fact = KernelMF(n_factors=50, verbose=0, min_rating=1)
		self.matrix_fact.fit(self.users_data, self.ratings)

	def login_user(self, username):
		"""
		login a given user, and load data if the user already exists.
		:param username:
		"""
		if username in self.users:
			pass
		else:
			self.users[username] = self.items.copy()
		self.cur_user = username
		self.cur_recommendation = []

	def get_recommendations(self, num_of_recommendations):
		"""
		recommend to the logged user according to he's collected data
		:return: a list with size num_of_recommendations of the cur_user's most recommended items
		"""
		if len(self.cur_recommendation) == 0:
			items_known = self.users_data_for_update.query("user_id == @self.cur_user")["item_id"]
			recommendations_df = self.matrix_fact.recommend(user=self.cur_user, items_known=items_known, amount=num_of_recommendations)
			print(recommendations_df)
			self.cur_recommendation = [int(item[1:]) for item in recommendations_df["item_id"]]
		return self.cur_recommendation

	def update_ratings(self, items, ratings): #ratings):
		"""
		use the given ratings to update the model
		:param ratings:
		:return:
		"""
		user_id = [self.cur_user for i in range(len(items))]
		self.users_data_for_update = pd.concat([self.users_data_for_update, pd.DataFrame(data={"user_id": user_id, "item_id": items, "rating": ratings})],
											   ignore_index=True).astype({"rating": np.int64})
		self.matrix_fact.update_users(self.users_data_for_update[["user_id", "item_id"]], self.users_data_for_update["rating"], verbose=0)
		self.cur_recommendation = []

	def get_item_for_rating(self):
		"""
		get random item that the current user hasn't rated yet
		:return:
		"""
		if self.cur_user == "":
			return self.items[np.random.randint(0, len(self.items))]
		if len(self.users[self.cur_user]) == 0:
			self.users[self.cur_user] = self.items.copy()
		random_index = np.random.randint(0, len(self.users[self.cur_user]))
		return self.users[self.cur_user].pop(random_index)
