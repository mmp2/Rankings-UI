from tkinter import *
from tkinter import ttk
import sys

from matplotlib.pyplot import text
from Proposal import Proposal
from Ranking import Ranking

class GUI:
    def __init__(self, Ranking) -> None:
        self.rankings = Ranking

        self.root = Tk()
        self.root.title('Rankings UI')
        self.root.geometry('800x500')
        self.root['bg'] = '#AC99F2' # Background Color of the entire UI

        # Set Scroll Bar
        self.scrlbar2 = ttk.Scrollbar(self.root)
        self.scrlbar2.pack(side="right", fill="y")

        self.scrlbar = ttk.Scrollbar(self.root,orient ='horizontal')
        self.scrlbar.pack(side="bottom", fill="x")

        self.columns = self.rankings.get_columns()

        # Create treeview with columns. Display all columns
        self.tree = ttk.Treeview(self.root,yscrollcommand=self.scrlbar2.set, height = 33, columns=self.columns, xscrollcommand=self.scrlbar.set, show='headings')

        # treeview to show column motion
        self.visual_drag = ttk.Treeview(self.root, yscrollcommand=self.scrlbar2.set, height = 33, columns=self.columns, xscrollcommand=self.scrlbar.set, show='headings')
        self.tree.pack()
        self.pos_to_prop_dict = {}
        self.viewer_prop_to_review = {}
        self.scrlbar2.config(command=self.tree.yview)
        self.scrlbar.config(command=self.tree.xview)
        self.initilize_items()


    def init_reviews(self, list_reviews):
        #nums_rows = self.rankings.get_num_rows()
        for review in list_reviews:
            self.viewer_prop_to_review[(review.reviewer, review.proposal)] = review.text

    def initilize_items(self):
        vertical_rankings = self.rankings.get_vertical_rankings()
        nums_rows = self.rankings.get_num_rows()
        # Set headers
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.visual_drag.heading(col, text=col)

    # insert some items into the tree
        for i in range(nums_rows):
            self.tree.insert('', 'end', iid='line%i' % i,
                        values=tuple(vertical_rankings[i]))
            self.visual_drag.insert('', 'end', iid='line%i' % i,
                            values=tuple(vertical_rankings[i]))
            for j in range(len(vertical_rankings[i])):
                self.pos_to_prop_dict[(i, j)] = vertical_rankings[i][j]

    
    def init_proposals(self, text):
        pass

    def bDown(self, event):
        global col_from, dx, col_from_id
        tv = event.widget
        if tv.identify_region(event.x, event.y) != 'separator':
            col = tv.identify_column(event.x)
            col_from_id = tv.column(col, 'id')
            col_from = int(col[1:]) - 1  # subtract 1 because display columns array 0 = tree column 1
            # get column x coordinate and width
            bbox = tv.bbox(tv.get_children("")[0], col_from_id)
            dx = bbox[0] - event.x  # distance between cursor and column left border
            tv.heading(col_from_id, text='')
            self.visual_drag.configure(displaycolumns=[col_from_id])
            self.visual_drag.place(in_=tv, x=bbox[0], y=0, anchor='nw', width=bbox[2], relheight=1)
        else:
            col_from = None

    def bUp(self, event):
        tv = event.widget
        col_to = int(tv.identify_column(event.x)[1:]) - 1  # subtract 1 because display columns array 0 = tree column 1
        self.visual_drag.place_forget()
        if col_from is not None:
            tv.heading(col_from_id, text=self.visual_drag.heading('#1', 'text'))
            if col_from != col_to:
                dcols = list(tv["displaycolumns"])
                if dcols[0] == "#all":
                    dcols = list(tv["columns"])

                if col_from > col_to:
                    dcols.insert(col_to, dcols[col_from])
                    dcols.pop(col_from + 1)
                else:
                    dcols.insert(col_to + 1, dcols[col_from])
                    dcols.pop(col_from)
                tv.config(displaycolumns=dcols)

    def bMotion(self, event):
        # drag around label if visible
        if self.visual_drag.winfo_ismapped():
            self.visual_drag.place_configure(x=dx + event.x)


    def closeWindow(self):
        self.root.destroy()
        sys.exit()
    
    def do_popup(self, event):
        self.popup = Menu(self.root, tearoff=0)
        self.popup.add_command(label="Review Details", command=lambda: self.review_detail(event))
        self.popup.add_command(label="Proposal Details", command=lambda: self.proposal_detail(event)) # , command=next) etc...

        self.popup.add_separator()
        self.popup.add_command(label="Exit", command=lambda: self.closeWindow())
        try:
            self.popup.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup.grab_release()

    def review_detail(self, event):
        row = int(self.tree.identify_row(event.y)[-1])
        col = int(self.tree.identify_column(event.x)[-1])
        proposal = self.pos_to_prop_dict[(row, col)]
        self.child_window("Review Details")


    def child_window(self, text):
        win2 = Toplevel()
        #text = "This is the child window"
        Label(win2, text=text).pack()
        element_header=['1st','2nd','3rd']
        treeScroll = ttk.Scrollbar(win2)
        treeScroll.pack(side=RIGHT, fill=Y)
        tree = ttk.Treeview(win2,columns=element_header, show="headings", yscrollcommand = treeScroll)
        tree.heading("1st", text="1st")
        tree.pack(side=LEFT, fill=BOTH)
        treeScroll.config(command=tree.yview)


    def proposal_detail(self, event):

        #print(type(self.tree.identify_row(event.y)))
        row = int(self.tree.identify_row(event.y)[-1])
        col = int(self.tree.identify_column(event.x)[-1])
        proposal = self.pos_to_prop_dict[(row, col)]
        self.child_window("Proposal Details")
        #print('clicked item:', row, " ", col)
        #text = self.viewer_prop_to_review[()]
        #label.config(text="Hello")
    
    def color_box(self, row, col, color):
        # TODO
        pass
    
    def show(self):
        self.tree.bind("<Button-3>", self.do_popup)
        self.tree.bind("<ButtonPress-1>", self.bDown)
        self.tree.bind("<ButtonRelease-1>",self.bUp)
        self.tree.bind("<Motion>",self.bMotion)
        self.root.mainloop()

