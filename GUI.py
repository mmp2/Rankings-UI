from tkinter import *
from tkinter import ttk
import tkinter as tk
import sys
#import tkinter.ttk as ttk
import tkinter.font as tkFont

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
    def __init__(self, ranking_path, reviews_path, op_path, ratings_paths) -> None:
        self.rankings = rankings(ranking_path, op_path, ratings_paths)
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

        self.intial_canvas()


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
                    self.pos[keys[i], op_dict[keys[i]][rates[j]][k]] = (i*200, i*200+180, 40+(5-rate)*20*num_most+k*20, 60+(5-rate)*20*num_most+k*20)
        self.lines_pos = []
        for rate in range(5):
            self.lines_pos.append((0, 30+rate*20*num_most, 2200, 30+rate*20*num_most))


    def intial_canvas(self):
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="white", yscrollcommand=self.scrlbar2.set, xscrollcommand=self.scrlbar.set,
                                confine=False, scrollregion=(0,0,1000,600))
        reviewer_boxes = []
        self.get_all_pos()
        for i in range(len(self.columns)):
            box = Proposal_Box(self.canvas, self.columns[i], (i*200, i*200+180, 0, 20))
            reviewer_boxes.append(box)
        for pair in self.pos.keys():   
            color = self.get_color(pair[0], pair[1])
            box = Proposal_Box(self.canvas, pair[1], self.pos[pair], color)
        for line in self.lines_pos:
            self.canvas.create_line(line[0], line[1], line[2], line[3], width=1.5)
        self.canvas.pack()
        self.scrlbar2.config(command=self.canvas.yview)
        self.scrlbar.config(command=self.canvas.xview)
    #def init_rect(self):



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

    def show(self):
        #self.tree.bind("<Button-3>", self.do_popup)
        #self.tree.bind("<ButtonPress-1>", self.bDown)
        #self.tree.bind("<ButtonRelease-1>",self.bUp)
        #self.tree.bind("<Motion>", self.bMotion)
        #self.tree.bind('<ButtonRelease-1>', self.selectItem)
        #self.tree.bind('<Button-3>', self.selectItem)
        self.canvas.pack()
        self.root.mainloop()