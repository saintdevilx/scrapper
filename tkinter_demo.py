# import everything from tkinter module 
from tkinter import *

# globally declare the expression variable 
expression = "" 
import Tkinter, Tkconstants, tkFileDialog

from scrapper import Scrapper

FILE_NAME=None
SELENIUM=True
TEST=False
URL=None
sel_var=None
test_var=None
def browsefunc():
	global FILE_NAME
	filename = tkFileDialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
	FILE_NAME=filename


def start_scraper():
	global SELENIUM
	global FILE_NAME
	global TEST
	kwargs ={
		'selenium':SELENIUM,
		'url':FILE_NAME,
		'test':TEST	,
		'skip_after':0,
		'skip_before':0,
		'export':'json'
	}
	if not TEST:
		print('test not enabled...')
		Scrapper(**kwargs).crawl()
	else:
		Scrapper.test()

# Driver code 
if __name__ == "__main__": 
	# create a GUI window 
	gui = Tk() 
	global sel_var
	global test_var
	sel_var=IntVar()
	test_var=IntVar()

	def toggle_selenium():
		global SELENIUM
		SELENIUM = sel_var.get()

	def toggle_test():
		global TEST
		TEST = test_var.get()

	# set the title of GUI window 
	gui.title("Ops Expert Scraper Tool") 

	# set the configuration of GUI window 
	gui.geometry("500x300") 

	file_chooser = Button(gui, text=' Choose file to upload ', fg='black', 
					command=lambda: browsefunc(), height=1, width=7) 
	file_chooser.grid(row=2, column=1) 


	selenium_check = Checkbutton(gui, text='Selenium', fg='black', 
					command=lambda: toggle_selenium(), height=1, width=7,onvalue=True, offvalue=False,  variable=sel_var) 
	selenium_check.grid(row=2, column=2) 


	
	test_run = Checkbutton(gui, text='Test Run !', fg='black', 
					command=lambda: toggle_test(),onvalue=True, offvalue=False, height=1, width=7,variable=test_var) 
	test_run.grid(row=2, column=3) 

	start_button = Button(gui, text='Start',command=lambda:start_scraper(), height=5,width=10)
	start_button.grid(row=3,column=3)

	skip_before = Entry(gui, bd =2)
	skip_before.grid(row=4,column=3)
	skip_after = Entry(gui, bd =2)
	skip_after.grid(row=5,column=3)
 
	gui.mainloop() 
