from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
import sys

class filter_window:
    def __init__(self, gui, attr, score_range, num_papers) -> None:
        self.gui = gui
        self.root2 = Tk()
        self.root2.title('Filter Window for Rankings UI')
        self.root2.geometry('500x400+100+150')
        
        self.score_range = score_range
        self.num_papers = num_papers
        self.dict = attr
        self.ratings = list(attr.keys())
        self.var_min = []
        self.var_max = []
        self.tkvarq_topk = StringVar(self.root2)
        self.tkvarq_topk.set("Please Select a Topk")
        for i in range(len(self.ratings)):
            tkvarq_max = StringVar(self.root2)
            tkvarq_min = StringVar(self.root2)
            tkvarq_max.set("Please Select a Maximum")
            tkvarq_min.set("Please Select a Minimum")
            self.var_max.append(tkvarq_max)
            self.var_min.append(tkvarq_min)
            self.create_wigets(self.ratings[i], i)

        submit_button = Button(self.root2, text="Submit and Reopen the Main Window", command=self.return_pairs)
        paddings = {'padx': 2, 'pady': 5}
        submit_button.grid(column=1, row=len(self.ratings)+2)
        label_min = ttk.Label(self.root2, text=f'Minimum Score')
        label_min.grid(column=1, row=0, sticky=tk.W, **paddings)
        label_max = ttk.Label(self.root2, text=f'Maximum Score')
        label_max.grid(column=2, row=0, sticky=tk.W, **paddings)

        label_topk = ttk.Label(self.root2, text=f'Top-K Rankings:')
        label_topk.grid(column=0, row=len(self.ratings)+1, sticky=tk.W, **paddings)
        #label2 = ttk.Label(self.root2, text=f'Minimum Score of {ga}:')
        #label2.grid(column=2, row=order, sticky=tk.W, **paddings)
        # option menu
        option_menu_topk = ttk.OptionMenu(
            self.root2,
            self.tkvarq_topk,
            None,
            *range(1, self.num_papers+1))
        option_menu_topk.grid(column=1, row=len(self.ratings)+1, sticky=tk.W, **paddings)
        
    def create_wigets(self, ga, order):
        # padding for widgets using the grid layout
        paddings = {'padx': 2, 'pady': 5}

        # label
        label1 = ttk.Label(self.root2, text=f'{ga}:')
        label1.grid(column=0, row=order+1, sticky=tk.W, **paddings)
        #label2 = ttk.Label(self.root2, text=f'Minimum Score of {ga}:')
        #label2.grid(column=2, row=order, sticky=tk.W, **paddings)
        # option menu
        option_menu_max = ttk.OptionMenu(
            self.root2,
            self.var_max[order],
            str(max(self.dict[ga])),
            *self.score_range)
        option_menu_min = ttk.OptionMenu(
            self.root2,
            self.var_min[order],
            str(min(self.dict[ga])),
            *self.score_range)
        '''
        else:
            option_menu_max = ttk.OptionMenu(
                self.root2,
                self.var_max[order],
                max(self.score_range),
                *self.score_range)

            option_menu_min = ttk.OptionMenu(
                self.root2,
                self.var_min[order],
                min(self.score_range),
                *self.score_range)
        '''
        option_menu_max.grid(column=2, row=order+1, sticky=tk.W, **paddings)
        option_menu_min.grid(column=1, row=order+1, sticky=tk.W, **paddings)
        # output label
        #self.output_label = ttk.Label(self.root2, foreground='red')
        #self.output_label.grid(column=0, row=1, sticky=tk.W, **paddings)


    def return_pairs(self):
        self.result = {}
        valid = True
        for i in range(len(self.ratings)):
            min = self.var_min[i].get()
            max = self.var_max[i].get()
            if int(min) > int(max):
                messagebox.showerror(title="Illegal Values", message="Minimun cannot be larger than the maximum.")     
                valid = False
                break 
            self.result[self.ratings[i]] = [int(self.var_min[i].get()), int(self.var_max[i].get())]
        if valid:
            self.gui.filter_ratings(self.result, int(self.tkvarq_topk.get()))

        '''
        pairs = list(i.get() for i in self.var_list if i.get() != "None")
        if len(set(pairs)) == len(pairs):
            for i in range(len(self.var_list)):
                self.result[self.graph_attr[i]] = self.var_list[i].get()
            self.gui.update_all_rects(self.result)
        else:
            messagebox.showerror(title="Illegal Matching", message="Please Make Sure to Assign every Rating to Only One Graphical Attribute.")        
        '''
    
    def show(self):
        self.root2.mainloop()

    def get_pair(self):
        return self.result


ratings = {"Overall Score": ['0', '5'],
    "Relevance and Significance": ['0', '5'],
    "Novelty": ['0', '5'],
    "Technical Quality": ['0', '5'], 
    "Experimental Evaluation": ['0', '5']}
#inst = filter_window(ratings, range(6)).show()

