from PIL import ImageTk, Image

from tkinter import (Tk, Label, Button, Radiobutton, Frame, Menu, StringVar, Entry, END)
from tkinter import messagebox
import time
from recommenderBaseModelItemBased import RecommenderBaseModel

BACKGROUND_COLOR = "#FFFAE7"
BACKGROUND_COLOR_2 = "#FAE8C4"
TEXT_COLOR = "#E59824"
FONT = "Hoefler Text"
answers_list = []

RATING_SEQUENCE_LENGTH = 5
NUM_OF_RECOMMENDED_ITEMS = 4


def get_item_id(item_indx):
	"""
	get itemId based on item's index
	"""
	return 'i' + str(item_indx)


def dialogBox(title, message):
	"""
	Basic function to create and display general dialog boxes.
	"""
	dialog = Tk()
	dialog.wm_title(title)
	dialog.grab_set()
	dialogWidth, dialogHeight = 225, 125
	positionRight = int(dialog.winfo_screenwidth() / 2 - dialogWidth / 2)
	positionDown = int(dialog.winfo_screenheight() / 2 - dialogHeight / 2)
	dialog.geometry("{}x{}+{}+{}".format(
		dialogWidth, dialogHeight, positionRight, positionDown))
	dialog.maxsize(dialogWidth, dialogHeight)
	label = Label(dialog, text=message)
	label.pack(side="top", fill="x", pady=10)
	ok_button = Button(dialog, text="Ok", command=dialog.destroy)
	ok_button.pack(ipady=3, pady=10)
	dialog.mainloop()


def finishedDialog(title, message):
	"""
	Display the finished dialog box when user reaches the end of the survey.
	"""
	dialog = Tk()
	dialog.wm_title(title)
	dialog.grab_set()
	dialogWidth, dialogHeight = 325, 150
	positionRight = int(dialog.winfo_screenwidth() / 2 - dialogWidth / 2)
	positionDown = int(dialog.winfo_screenheight() / 2 - dialogHeight / 2)
	dialog.geometry("{}x{}+{}+{}".format(
		dialogWidth, dialogHeight, positionRight, positionDown))
	dialog.maxsize(dialogWidth, dialogHeight)
	dialog.update_idletasks()
	dialog.overrideredirect(True)
	label = Label(dialog, text=message)
	label.pack(side="top", fill="x", pady=10)
	ok_button = Button(dialog, text="Quit", command=quit)
	ok_button.pack(ipady=3, pady=10)
	dialog.mainloop()


class RecommenderVisualInterface(Tk):
	"""
	Main class, define the container which will contain all the frames.
	"""

	def __init__(self, *args, **kwargs):
		Tk.__init__(self, *args, **kwargs)

		# call closing protocol to create dialog box to ask if user if they want to quit or not.
		self.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.recommender_model = RecommenderBaseModel('ratings.csv', True)

		self.imgs_dict = {i: ImageTk.PhotoImage(Image.open('imgs/Picture' + str(i) + '.png')) for i in range(1, 61)}
		self.header_img = ImageTk.PhotoImage(Image.open("imgs/header.png"))

		Tk.wm_title(self, "Second-Hand Clothing Recommender")

		# get position of window with respect to screen
		windowWidth, windowHeight = 1000, 600
		positionRight = int(Tk.winfo_screenwidth(self) / 2 - windowWidth / 2)
		positionDown = int(Tk.winfo_screenheight(self) / 2 - windowHeight / 2)
		Tk.geometry(self, newGeometry="{}x{}+{}+{}".format(windowWidth, windowHeight, positionRight, positionDown))
		Tk.maxsize(self, windowWidth, windowHeight)

		# Create container Frame to hold all other classes,
		# which are the different parts of the survey.
		container = Frame(self)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		# Create menu bar
		menubar = Menu(container)
		filemenu = Menu(menubar, tearoff=0)
		filemenu.add_command(label="Quit", command=quit)
		menubar.add_cascade(label="File", menu=filemenu)

		Tk.config(self, menu=menubar)

		# create empty dictionary for the different frames (the different classes)
		self.frames = {}

		for fr in (LoginPage, WelcomePage, RatingPage, RecommendPage):
			frame = fr(container, self)
			self.frames[fr] = frame
			frame.grid(row=0, column=0, sticky="nsew")

		self.show_frame(LoginPage)

	def on_closing(self):
		"""
		Display dialog box before quitting.
		"""
		if messagebox.askokcancel("Quit", "Do you want to quit?"):
			self.destroy()

	def login_user(self, username):
		self.recommender_model.login_user(username)
		self.frames[WelcomePage].set_username(username)

	def update_users_ratings(self, items, ratings):
		self.recommender_model.update_ratings(items, ratings)

	def get_recommended_items(self):
		return self.recommender_model.get_recommendations(NUM_OF_RECOMMENDED_ITEMS)

	def get_item_to_rate(self):
		return self.recommender_model.get_item_for_rating()

	def show_frame(self, cont):
		"""
		Used to display a frame.
		"""
		frame = self.frames[cont]
		if cont.__name__ == 'RecommendPage':
			frame.update_recommendation()
		frame.tkraise()  # bring a frame to the "top"


class LoginPage(Frame):
	"""
	First page that user will see: Login Page.
	"""
	def __init__(self, master, controller):
		Frame.__init__(self, master)
		self.controller = controller

		# login page header:
		self.configure(bg=BACKGROUND_COLOR)
		self.header_image = Label(self, image=controller.header_img, borderwidth=0, bg=BACKGROUND_COLOR)
		self.header_image.pack()

		info_text = "Login Page"
		info_label = Label(self, text=info_text, font=(FONT, 20), bg=BACKGROUND_COLOR, fg=TEXT_COLOR, relief="flat")
		info_label.pack(pady=(10, 50), padx=10, ipadx=20, ipady=3)

		# username box:
		user = Label(self, text="Please enter username:", font=(FONT, 14), bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
					 relief="flat")
		user.pack(pady=1, padx=1, ipadx=5, ipady=3)
		self.username = Entry(self, font=(FONT, 14))
		self.username.pack()

		# continue/quit buttons
		b_frame = Frame(self, borderwidth=0, relief="ridge", bg=BACKGROUND_COLOR)
		b_frame.pack(pady=(70, 10), anchor='center')

		start_button = Button(b_frame, text="continue", command=self.save_username, font=(FONT, 14),
							  fg=TEXT_COLOR)
		start_button.pack(side='right', ipady=7, padx=20)
		quit_button = Button(b_frame, text="quit", command=self.on_closing, font=(FONT, 14), fg=TEXT_COLOR)
		quit_button.pack(side='left', ipady=7, ipadx=15, padx=50)

	def save_username(self):
		self.controller.login_user(self.username.get())
		self.username.delete(0, END)
		self.controller.show_frame(WelcomePage)

	def on_closing(self):
		"""
		Display dialog box before quitting.
		"""
		if messagebox.askokcancel("Quit", "Do you want to quit?"):
			self.controller.destroy()


class WelcomePage(Frame):
	"""
	Second page that user will see: welcome page.
	description and explanations.
	"""
	def __init__(self, master, controller):
		Frame.__init__(self, master)
		self.controller = controller

		# set up start page window
		self.configure(bg=BACKGROUND_COLOR)
		self.header_image = Label(self, image=controller.header_img, borderwidth=0, bg=BACKGROUND_COLOR)
		self.header_image.pack()

		# add labels and buttons to window
		self.welcome_label = Label(self, text="", font=(FONT, 18), bg=BACKGROUND_COLOR, fg=TEXT_COLOR, relief="flat")
		self.welcome_label.pack(pady=10, padx=10, ipadx=20, ipady=10)

		# add labels and buttons to window
		info_text = "This recommendation system is designed to offer you second-hand clothing items based on your" \
					" personal taste,\nto create an easier shopping experience for you.\n\nAll items are taken from" \
					" Chen Galdan's second-hand clothing online store.\n\n\nIf it's your first time here, start rating" \
					" items to let the system learn your preferences. click on 'rate items'.\nWhenever you would" \
					" like to, you can always click on 'get recommendations' button to see the items the system" \
					" offers for you."
		self.info_label = Label(self, text=info_text, font=(FONT, 14), bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
								relief="flat")
		self.info_label.pack(pady=10, padx=10, ipadx=20, ipady=3)

		# buttons:
		b_frame = Frame(self, borderwidth=0, relief="ridge", bg=BACKGROUND_COLOR)
		b_frame.pack(pady=(70, 10), anchor='center')

		rate_button = Button(b_frame, text="rate items", font=(FONT, 14), fg=TEXT_COLOR,
							 command=lambda: controller.show_frame(
								 RatingPage))  # , highlightbackground=BACKGROUNG_COLOR_2)
		rate_button.pack(side='right', ipady=7, ipadx=15, padx=50)
		recommend_button = Button(b_frame, text="get recommendations",
								  command=lambda: controller.show_frame(RecommendPage), font=(FONT, 14), fg=TEXT_COLOR)
		recommend_button.pack(side='right', ipady=7, ipadx=15, padx=50)
		quit_button = Button(b_frame, text="logout", command=lambda: controller.show_frame(LoginPage), font=(FONT, 14),
							 fg=TEXT_COLOR)
		quit_button.pack(side='right', ipady=7, ipadx=15, padx=50)

	def set_username(self, username):
		"""
		set the username of the current user to present on the screen
		"""
		info_text = "Welcome " + username + "!"
		self.welcome_label.configure(text=info_text)

	def on_closing(self):
		"""
		Display dialog box before quitting.
		"""
		if messagebox.askokcancel("Quit", "Do you want to quit?"):
			self.controller.destroy()


class RatingPage(Frame):
	"""
	Class that the page of rating an item
	"""
	def __init__(self, master, controller):
		Frame.__init__(self, master)
		self.controller = controller
		self.configure(bg=BACKGROUND_COLOR)
		self.cnt = 0

		self.img_indx = self.controller.get_item_to_rate()
		self.length_of_list = RATING_SEQUENCE_LENGTH
		self.rated_items = []
		self.ratings = []

		# Create header label
		self.header_image = Label(self, image=controller.header_img, borderwidth=0, bg=BACKGROUND_COLOR)
		self.header_image.pack()

		# set image of the item
		self.item_image = Label(self, image=controller.imgs_dict[self.img_indx], borderwidth=0, bg=BACKGROUND_COLOR)
		self.item_image.pack()

		Label(self, text="rate the given item:", font=(FONT, 10), bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
			  relief="flat").pack(padx=50, pady=(20, 1))

		scale = [("1", 1), ("2", 2), ("3", 3), ("4", 4), ("5", 5)]

		self.var = StringVar()
		self.var.set(0)  # initialize

		# Frame to contain checkboxes
		checkbox_frame = Frame(self, borderwidth=1, relief="flat", bg=BACKGROUND_COLOR)
		checkbox_frame.pack(pady=(1, 10), anchor='s')

		for text, value in scale:
			b = Radiobutton(checkbox_frame, text=text, variable=self.var, value=value, bg=BACKGROUND_COLOR_2,
							foreground=TEXT_COLOR, selectcolor='white')
			b.pack(side='left', ipadx=20, ipady=2)

		# next item button:
		enter_button = Button(self, text="Next Item", font=(FONT, 14), fg=TEXT_COLOR, command=self.nextQuestion)
		enter_button.pack(ipady=5, pady=20, anchor='s')

		# buttons:
		b_frame = Frame(self, borderwidth=0, relief="ridge", bg=BACKGROUND_COLOR)
		b_frame.pack(anchor='center')
		recommend_button = Button(b_frame, text="get recommendations",
								  command=lambda: self.quit_ratings(func=lambda: controller.show_frame(RecommendPage)),
								  font=(FONT, 14), fg=TEXT_COLOR)
		recommend_button.pack(side='right', ipady=7, ipadx=15, padx=(400, 1))
		quit_button = Button(b_frame, text="logout",
							 command=lambda: self.quit_ratings(func=lambda: controller.show_frame(LoginPage)),
							 font=(FONT, 14), fg=TEXT_COLOR)
		quit_button.pack(side='left', ipady=7, ipadx=15, padx=(1, 100))

	def nextQuestion(self):
		"""
		When button is clicked, save user's rating and display next question.
		"""
		answer = self.var.get()
		if answer == '0':
			dialogBox("No Value Given", "You did not rate the item,\nPlease try again.")

		else:
			self.cnt = (self.cnt + 1)
			self.rated_items.append(get_item_id(self.img_indx))
			self.ratings.append(answer)

			if self.cnt == self.length_of_list:
				self.quit_ratings(func=lambda: self.controller.show_frame(RecommendPage))

			else:
				self.img_indx = self.controller.get_item_to_rate()
				self.item_image.config(image=self.controller.imgs_dict[self.img_indx])
				self.var.set(0)  # reset value for next question
				time.sleep(.2)  # delay between items

	def quit_ratings(self, func):
		"""
		when quitting the rating page, process the rated items in this session.
		:param func: function to operate after
		"""
		answer = self.var.get()
		# if answer != '0' and self.img_indx not in self.ratings_dict:
		if answer != '0' and (len(self.rated_items) == 0 or get_item_id(self.img_indx) != self.rated_items[-1]):
			# self.ratings_dict[self.img_indx] = answer
			self.rated_items.append(get_item_id(self.img_indx))
			self.ratings.append(answer)
		if len(self.rated_items) > 0:
			self.controller.update_users_ratings(self.rated_items, self.ratings)  # self.ratings_dict)
			self.rated_items = []
			self.ratings = []
			self.cnt = 0
			self.var.set(0)
			self.img_indx = self.controller.get_item_to_rate()
			self.item_image.config(image=self.controller.imgs_dict[self.img_indx])
		func()


class RecommendPage(Frame):
	"""
	Page for the recommended items
	"""
	def __init__(self, master, controller):
		Frame.__init__(self, master)
		self.controller = controller

		# set up start page window
		self.configure(bg=BACKGROUND_COLOR)
		self.header_image = Label(self, image=controller.header_img, borderwidth=0, bg=BACKGROUND_COLOR)
		self.header_image.pack()

		# add labels and buttons to window
		info_text = "Your recommended items:"
		self.info_label = Label(self, text=info_text, font=(FONT, 14), bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
								relief="flat")
		self.info_label.pack(pady=10, padx=10, anchor='nw')

		imgs_frame = Frame(self, borderwidth=0, relief="ridge", bg=BACKGROUND_COLOR)
		imgs_frame.pack(anchor='center')

		self.imgs = []
		self.imgs_labels = []
		for i in range(1, NUM_OF_RECOMMENDED_ITEMS + 1):
			self.imgs.append(self.controller.imgs_dict[i])
			self.imgs_labels.append(Label(imgs_frame, image=self.imgs[-1], borderwidth=0, bg=BACKGROUND_COLOR))
			self.imgs_labels[-1].pack(pady=20, padx=10, side='right')

		# continue/quit buttons
		b_frame = Frame(self, borderwidth=0, relief="ridge", bg=BACKGROUND_COLOR)
		b_frame.pack(anchor='center')

		start_button = Button(b_frame, text="rate more items", font=(FONT, 14), fg=TEXT_COLOR,
							  command=lambda: controller.show_frame(RatingPage))
		start_button.pack(side='right', ipady=7, padx=(400, 1), pady=40)
		quit_button = Button(b_frame, text="logout", command=lambda: controller.show_frame(LoginPage), font=(FONT, 14),
							 fg=TEXT_COLOR)
		quit_button.pack(side='left', ipady=7, ipadx=15, padx=(1, 100), pady=40)

	def update_recommendation(self):
		recommended_items = self.controller.get_recommended_items()
		for i in range(len(recommended_items)):
			self.imgs[i] = self.controller.imgs_dict[recommended_items[i]]
			self.imgs_labels[i].config(image=self.imgs[i])


# Run program
if __name__ == "__main__":
	app = RecommenderVisualInterface()
	app.mainloop()
