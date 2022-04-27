from tkinter import *
from tkinter import ttk
import tkinter as tk
import sys

import numpy as np
from Proposal import Proposal
from Ranking import rankings
from Review import review
from Ratings import ratings
from Proposal_Box import Proposal_Box

FQ_COLOR_DICT = {
    5 : "lightgreen",
    4 : "lightblue",
    1 : "gainsboro",
    2 : "yellow",
    3 : "pink",
    0 : "white"
}

class GUI:
    def __init__(self, ranking_path, reviews_path, ratings_paths) -> None:
        self.rankings = rankings(ranking_path, ratings_paths)
        self.reviews = review(reviews_path)

        self.root = Tk()
        self.root.title('Rankings UI')
        self.root.geometry('800x600')
        self.root['bg'] = '#AC99F2' # Background Color of the entire UI

        # Set Scroll Bar
        self.scrlbar2 = ttk.Scrollbar(self.root)
        self.scrlbar2.pack(side="right", fill="y")

        self.scrlbar = ttk.Scrollbar(self.root, orient ='horizontal')
        self.scrlbar.pack(side="bottom", fill="x")

        self.columns = self.rankings.get_columns()
        self.overall_rankings = self.rankings.get_all_rankings()
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="white", yscrollcommand=self.scrlbar2.set, xscrollcommand=self.scrlbar.set,
                        confine=False, scrollregion=(0,0,1000,600))
        #button1 = Button(self.root, text="Switch To Left")
        #button1.place(x=25, y=100)
        self.canvas.pack()
        self.scrlbar2.config(command=self.canvas.yview)
        self.scrlbar.config(command=self.canvas.xview)

        self.intial_canvas()
        #self.init_buttons()
        self.init_number()
        self.set_up()

    def init_number(self):
        for i in range(1, 6):
            Label(self.root,text=str(i),font=("Arial", 25)).place(x=0, y=self.lines_pos[i-1][1])

    def init_buttons(self):
        but_list = []
        for i in range(len(self.columns)):
            button = Button(self.root, text="Switch To Left")
            button.place(x=i*200, y=20)
            but_list.append(button)
            #box = Proposal_Box(self.canvas, reviewer=self.columns[i], pos=(i*200, i*200+180, 0, 20))

    def get_all_pos(self):
        op_dict, num_most = self.rankings.get_op_rankings()
        num_most += 1
        self.pos = {}
        keys = list(op_dict.keys())
        for i in range(len(keys)):
            rates = list(op_dict[keys[i]].keys())
            for j in range(len(rates)):
                rate = rates[j]
                for k in range(len(op_dict[keys[i]][rates[j]])):
                    self.pos[keys[i], op_dict[keys[i]][rates[j]][k]] = (i*200+50, i*200+230, 40+(5-rate)*20*num_most+k*20, 60+(5-rate)*20*num_most+k*20)
        self.lines_pos = []
        for rate in range(5):
            self.lines_pos.append((0, 30+rate*20*num_most, 2200, 30+rate*20*num_most))


    def intial_canvas(self):
        reviewer_boxes = []
        self.get_all_pos()
        for i in range(len(self.columns)):
            box = Proposal_Box(self.canvas, reviewer=self.columns[i], pos=(i*200+50, i*200+230, 0, 20))
            reviewer_boxes.append(box)
        for pair in self.pos.keys():   
            color = self.get_color(pair[0], pair[1])
            box = Proposal_Box(self.canvas, pair[0], self.pos[pair], pair[1], color)
        for line in self.lines_pos:
            self.canvas.create_line(line[0], line[1], line[2], line[3], width=1.5, fill="gray")

    def selectItem(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(x, y)

        _type = self.canvas.type(item)
        if _type != "rectangle":
            item  = (item[0]-1, )
        tags = self.canvas.gettags(item)
        prop = tags[1]
        self.canvas.itemconfig(prop, fill='Slategray4')

    def swap_left(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(x, y, halo=2)

        _type = self.canvas.type(item)
        if _type != "rectangle":
            item  = (item[0]-1, )
        tags = self.canvas.gettags(item)
        cur_rev = tags[0]
        index = self.columns.index(cur_rev)
        if index != 0:  
            left_rev = self.columns[index-1]
            self.canvas.move(left_rev, 200, 0)
            self.canvas.move(cur_rev+"text", -200, 0)
            self.canvas.move(left_rev+"text", 200, 0)
            self.canvas.move(cur_rev, -200, 0)

            self.columns[index] = left_rev
            self.columns[index-1] = cur_rev


    def get_color(self, reviewer, proposal):
        """
        returns the color of a given proposal box based on its FQ ranking.
        """
        return FQ_COLOR_DICT[self.rankings.get_fq_rating(reviewer, proposal)]
        

    def get_pos(self, reviewer, proposal):
        """
        returns the color of a given proposal box based on its OP ranking.
        """
        pass

    def closeWindow(self):
        self.root.destroy()
        sys.exit()
    
    def do_popup(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(x, y, halo=2)
        _type = self.canvas.type(item)
        if _type != "rectangle":
            item  = (item[0]-1, )
        tags = self.canvas.gettags(item)
        reviewer = tags[0]
        prop = tags[1]
        print(reviewer)
        print(prop)
        self.popup = Menu(self.root, tearoff=0)
        
        self.popup.add_command(label="Rating Details", command=lambda: self.rating_detail(reviewer, prop))
        self.popup.add_command(label="Review Text", command=lambda: self.review_text(reviewer, prop))
        self.popup.add_command(label="Proposal Details", command=lambda: self.proposal_detail(reviewer, prop)) # , command=next) etc...

        self.popup.add_separator()
        self.popup.add_command(label="Exit", command=lambda: self.closeWindow())
        try:
            self.popup.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup.grab_release()

    def rating_detail(self, reviewer, prop):
        self.child_window_ratings("Rating Details", reviewer, prop)


    def child_window_ratings(self, name, reviewer, proposal):
        win2 = Toplevel()
        Label(win2, text=name).pack()
        treeScroll = ttk.Scrollbar(win2)
        treeScroll.pack(side=RIGHT, fill=Y)
        col_names = self.rankings.get_all_sub_ratings()
        print(col_names)
        tree = ttk.Treeview(win2,columns=col_names, show="headings", yscrollcommand = treeScroll)
        rating = []
        for rate_name in col_names:
            rating.append(self.rankings.get_sub_rating(rate_name, reviewer, proposal))
        for col in col_names:
            tree.heading(col, text=col)
        print(rating)
        tree.insert('', 'end', iid='line1', values=tuple(rating))
        tree.pack(side=LEFT, fill=BOTH)
        treeScroll.config(command=tree.yview)


    def review_text(self, reviewer, proposal_name):
        text = self.reviews.get_review(reviewer, proposal_name)
        self.child_window_text(f"The Review of {proposal_name} by {reviewer}", text)

    def child_window_text(self, title, text):
        win2 = Toplevel()
        T = Text(win2, height=20, width=52)
        # Create label
        l = Label(win2, text=title)
        l.pack()
        T.pack()
        l.config(font =("Times", "24", "bold"))
        T.config(font =("Times", "16"))
        T.insert(tk.END, text)


    def set_up(self):
        self.canvas.bind("<Button-3>", self.do_popup)
        #self.tree.bind("<ButtonPress-1>", self.bDown)
        self.canvas.bind("<ButtonRelease-1>",self.ret_colors)
        #self.tree.bind("<Motion>", self.bMotion)
        self.canvas.bind('<Double-1>', self.swap_left) 
        self.canvas.bind('<ButtonPress-1>', self.selectItem)
        self.canvas.pack()

    def ret_colors(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(x, y, halo=2)

        _type = self.canvas.type(item)
        if _type != "rectangle":
            item  = (item[0]-1, )
        tags = self.canvas.gettags(item)
        prop = tags[1]
        all_items = self.canvas.find_withtag(prop)
        for item in all_items:
            reviewer = self.canvas.gettags(item)[0]
            self.canvas.itemconfig(item, fill=self.get_color(reviewer, prop))


    def show(self):
        self.root.mainloop()