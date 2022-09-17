from tkinter import *

class legend_window:
    def __init__(self, dict, gui, all_ratings) -> None:
        self.gui = gui
        self.root2 = Tk()
        self.root2.title('Legend Window for Rankings UI')
        self.root2.geometry('700x500+100+150')
        
        self.dict = dict
        self.graph_attr = list(dict.keys())
        self.ratings = all_ratings + ["None"]
        self.var_list = []
        
        for i in range(len(self.graph_attr)):
            tkvarq = StringVar(self.root2)
            tkvarq.set(self.dict[self.graph_attr[i]])
            self.var_list.append(tkvarq)
            self.create_wigets(self.graph_attr[i], i)

        submit_button = Button(self.root2, text="Submit and Reopen the Main Window", command=self.return_pairs)
        paddings = {'padx': 5, 'pady': 5}
        submit_button.grid(column=1, row=len(self.graph_attr)+1)
        
    def create_wigets(self, ga, order):
        # padding for widgets using the grid layout
        paddings = {'padx': 5, 'pady': 5}

        # label
        label = Label(self.root2, text=f'Please Select the Rating Displayed by the Graphical Attribute of {ga}:')
        label.grid(column=0, row=order, sticky=W, **paddings)

        # option menu
        option_menu = OptionMenu(
            self.root2,
            self.var_list[order],
            *self.ratings)
        option_menu.grid(column=1, row=order, sticky=W, **paddings)

    def return_pairs(self):
        self.result = {}
        pairs = list(i.get() for i in self.var_list if i.get() != "None")
        #if len(set(pairs)) == len(pairs):
        for i in range(len(self.var_list)):
            self.result[self.graph_attr[i]] = self.var_list[i].get()
        self.gui.update_all_rects(self.result)
        self.root2.destroy()

    def show(self):
        self.root2.mainloop()

    def get_pair(self):
        return self.result
