from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox

class filter_window:
    def __init__(self, gui, numerical_attr, yes_no_attr, score_range, num_papers, defalut_dict=None) -> None:
        self.gui = gui
        self.root2 = Tk()
        self.root2.title('Filter Window for Rankings UI')
        self.root2.geometry('500x400+100+150')
        self.score_range = score_range
        self.num_papers = num_papers
        self.dict = numerical_attr
        self.yesno_list = yes_no_attr
        self.ratings = list(numerical_attr.keys())
        self.var_min = []
        self.var_max = []

        self.yesno_var = []
        self.default_dict = defalut_dict
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

        for i in range(len(yes_no_attr)):
            tkvarq_yesno = StringVar(self.root2)
            tkvarq_yesno.set("Please Select Yes/No")
            self.yesno_var.append(tkvarq_yesno)
            self.create_wigets_yesno(i)

        submit_button = Button(self.root2, text="Submit and Reopen the Main Window", command=self.return_pairs)
        paddings = {'padx': 2, 'pady': 5}
        submit_button.grid(column=1, row=len(self.ratings)+3)
        label_min = ttk.Label(self.root2, text=f'Minimum Score')
        label_min.grid(column=1, row=0, sticky=tk.W, **paddings)
        label_max = ttk.Label(self.root2, text=f'Maximum Score')
        label_max.grid(column=2, row=0, sticky=tk.W, **paddings)

        label_topk = ttk.Label(self.root2, text=f'Top-K Rankings:')
        label_topk.grid(column=0, row=len(self.ratings)+len(self.yesno_list)+1, sticky=tk.W, **paddings)
        option_menu_topk = ttk.OptionMenu(
            self.root2,
            self.tkvarq_topk,
            str(self.default_dict["topk"]),
            *range(1, self.num_papers+1))
        option_menu_topk.grid(column=1, row=len(self.ratings)+len(self.yesno_list)+1, sticky=tk.W, **paddings)

    def create_wigets_yesno(self, order):
        # padding for widgets using the grid layout
        paddings = {'padx': 2, 'pady': 5}

        # label
        label_yesno = ttk.Label(self.root2, text=self.yesno_list[order])
        label_yesno.grid(column=0, row=len(self.ratings)+order+1, sticky=tk.W, **paddings)
        option_menu_req = ttk.OptionMenu(
            self.root2,
            self.yesno_var[order],
            self.default_dict[self.yesno_list[order]],
            *["Yes", "No"])
        option_menu_req.grid(column=1, row=len(self.ratings)+order+1, sticky=tk.W, **paddings)

    def create_wigets(self, label, order):
        # padding for widgets using the grid layout
        paddings = {'padx': 2, 'pady': 5}
        # label
        label1 = ttk.Label(self.root2, text=f'{label}:')
        label1.grid(column=0, row=order+1, sticky=tk.W, **paddings)
        option_menu_max = ttk.OptionMenu(
            self.root2,
            self.var_max[order],
            str(max(self.default_dict[label])),
            *self.score_range)
        option_menu_min = ttk.OptionMenu(
            self.root2,
            self.var_min[order],
            str(min(self.default_dict[label])),
            *self.score_range)

        option_menu_max.grid(column=2, row=order+1, sticky=tk.W, **paddings)
        option_menu_min.grid(column=1, row=order+1, sticky=tk.W, **paddings)


    def return_pairs(self):
        self.result = {}
        self.yesno_ret = {}
        valid = True
        for i in range(len(self.ratings)):
            min = self.var_min[i].get()
            max = self.var_max[i].get()
            if int(min) > int(max):
                messagebox.showerror(title="Illegal Values", message="Minimun cannot be larger than the maximum.")     
                valid = False
                break 
            self.result[self.ratings[i]] = [int(self.var_min[i].get()), int(self.var_max[i].get())]
        for j in range(len(self.yesno_list)):
            self.yesno_ret[self.yesno_list[j]] = str(self.yesno_var[j].get())
        if valid:
            self.gui.filter_ratings(self.result, self.yesno_ret, int(self.tkvarq_topk.get()))
            self.root2.destroy()
    
    def show(self):
        self.root2.mainloop()


