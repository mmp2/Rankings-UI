from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
import sys

class start_window:
    def __init__(self, graph_attr, ratings) -> None:
        self.root = Tk()
        self.root.title('Starter Window for Rankings UI')
        self.root.geometry('700x500+100+150')
        
        # Create the list of questions
        # Pass them into an option menu
        # Create an entry for the answer
        # Create submit button
        self.graph_attr = graph_attr
        self.ratings = ratings
        #self.tkvarq = StringVar(self.root) 
        self.var_list = []
        #self.tkvarq.set("Please Select a Rating")
        
        for i in range(len(graph_attr)):
            tkvarq = StringVar(self.root)
            tkvarq.set("Please Select a Rating")
            self.var_list.append(tkvarq)
            self.create_wigets(graph_attr[i], i)

        submit_button = Button(self.root, text="Submit and Open the Main Window",  command=self.return_pairs)
        paddings = {'padx': 5, 'pady': 5}
        submit_button.grid(column=1, row=len(graph_attr))
        #Answer entry
        #answer_entry = Entry(root, width=30)
        #answer_entry.pack()
        
    def create_wigets(self, ga, order):
        # padding for widgets using the grid layout
        paddings = {'padx': 5, 'pady': 5}

        # label
        label = ttk.Label(self.root, text=f'Please Select the Rating Displayed by the Graphical Attribute of {ga}:')
        label.grid(column=0, row=order, sticky=tk.W, **paddings)

        # option menu
        option_menu = ttk.OptionMenu(
            self.root,
            self.var_list[order],
            self.ratings[0],
            *self.ratings)

        option_menu.grid(column=1, row=order, sticky=tk.W, **paddings)

        # output label
        self.output_label = ttk.Label(self.root, foreground='red')
        self.output_label.grid(column=0, row=1, sticky=tk.W, **paddings)

    def return_pairs(self):
        self.result = {}
        if len(set(i.get() for i in self.var_list)) == len(self.var_list):
            for i in range(len(self.var_list)):
                self.result[self.graph_attr[i]] = self.var_list[i].get()
            self.root.destroy()
        else:
            messagebox.showerror(title="Illegal Matching", message="Please Make Sure to Assign every Rating to Only One Graphical Attribute.")

    def start(self):
        self.root.mainloop()
        return self.result
