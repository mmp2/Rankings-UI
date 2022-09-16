from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox

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
        self.tkvarq_req = StringVar(self.root2)
        self.tkvarq_req.set("Please")
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
        submit_button.grid(column=1, row=len(self.ratings)+3)
        label_min = ttk.Label(self.root2, text=f'Minimum Score')
        label_min.grid(column=1, row=0, sticky=tk.W, **paddings)
        label_max = ttk.Label(self.root2, text=f'Maximum Score')
        label_max.grid(column=2, row=0, sticky=tk.W, **paddings)

        label_rep = ttk.Label(self.root2, text=f'Reproducibility:')
        label_rep.grid(column=0, row=len(self.ratings)+1, sticky=tk.W, **paddings)
        option_menu_req = ttk.OptionMenu(
            self.root2,
            self.tkvarq_req,
            "Yes",
            *["Yes", "No"])
        option_menu_req.grid(column=1, row=len(self.ratings)+1, sticky=tk.W, **paddings)

        label_topk = ttk.Label(self.root2, text=f'Top-K Rankings:')
        label_topk.grid(column=0, row=len(self.ratings)+2, sticky=tk.W, **paddings)
        option_menu_topk = ttk.OptionMenu(
            self.root2,
            self.tkvarq_topk,
            str(num_papers),
            *range(1, self.num_papers+1))
        option_menu_topk.grid(column=1, row=len(self.ratings)+2, sticky=tk.W, **paddings)
        
    def create_wigets(self, ga, order):
        # padding for widgets using the grid layout
        paddings = {'padx': 2, 'pady': 5}

        # label
        label1 = ttk.Label(self.root2, text=f'{ga}:')
        label1.grid(column=0, row=order+1, sticky=tk.W, **paddings)
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

        option_menu_max.grid(column=2, row=order+1, sticky=tk.W, **paddings)
        option_menu_min.grid(column=1, row=order+1, sticky=tk.W, **paddings)


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
            self.gui.filter_ratings(self.result, str(self.tkvarq_req.get()), int(self.tkvarq_topk.get()))
            self.root2.destroy()

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


