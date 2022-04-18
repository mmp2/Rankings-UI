from tkinter import *
from tkinter import ttk
import tkinter as tk
import sys
#import tkinter.ttk as ttk
import tkinter.font as tkFont

from matplotlib.pyplot import text
from pkg_resources import IMetadataProvider
from Proposal import Proposal
from Ranking import rankings
from Review import review
from Ratings import ratings




class GUI:
    def __init__(self, ranking_path, reviews_path, ratings_paths) -> None:
        self.rankings = rankings(ranking_path)
        self.reviews = review(reviews_path)
        self.rating_names = list(ratings_paths.keys())
        self.ratings = {}
        for rate_name in ratings_paths.keys():
            self.ratings[rate_name] = ratings(ratings_paths[rate_name])

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

       #2. Create a Canvas Overlay to show selected Treeview cell 
        sel_bg = '#ecffc4'
        sel_fg = '#05640e'
        self.setup_selection(sel_bg, sel_fg)


    def setup_selection(self, sel_bg, sel_fg):
        self._font = tkFont.Font()

        self._canvas = tk.Canvas(self.tree,
                                 background=sel_bg,
                                 borderwidth=0,
                                 highlightthickness=0)

        self._canvas.text = self._canvas.create_text(0, 0,
                                                     fill=sel_fg,
                                                     anchor='w')



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
        #self.selectItem()
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
    
    def do_popup(self, event, col, proposal_name):
        #item = self.tree.identify_row(event.y)
        #print('clicked item:', item)
        #info = self.selectItem(event)
        #print(info)
        #col = info[0]
        #proposal_name = info[1]
        self.popup = Menu(self.root, tearoff=0)
        
        self.popup.add_command(label="Rating Details", command=lambda: self.rating_detail(col, proposal_name))
        self.popup.add_command(label="Review Text", command=lambda: self.review_text(col, proposal_name))
        self.popup.add_command(label="Proposal Details", command=lambda: self.proposal_detail(event)) # , command=next) etc...

        self.popup.add_separator()
        self.popup.add_command(label="Exit", command=lambda: self.closeWindow())
        try:
            self.popup.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup.grab_release()

    def review_text(self, col, proposal_name):
        reviewer = self.columns[col]
        text = self.reviews.get_review(reviewer, proposal_name)
        self.child_window_text(f"The Review of {proposal_name} by {reviewer}", text)

    def rating_detail(self, col, proposal_name):
        #row = int(self.visual_drag.identify_row(event.y)[-1])
        #col = int(self.visual_drag.identify_column(event.x)[-1])
        #print(col)
        #proposal = self.pos_to_prop_dict[(row, col)]
        reviewer = self.columns[col]
        self.child_window_ratings("Rating Details", reviewer, proposal_name)

    def child_window_text(self, title, text):
        print(title)
        win2 = Toplevel()
        #Label(win2, text=name).pack()
        T = Text(win2, height=20, width=52)
        # Create label
        l = Label(win2, text=title)
        l.pack()
        T.pack()
        l.config(font =("Times", "24", "bold"))
        T.config(font =("Times", "16"))
        T.insert(tk.END, text)

    def child_window_ratings(self, name, reviewer, proposal):
        win2 = Toplevel()
        #text = "This is the child window"
        Label(win2, text=name).pack()
        treeScroll = ttk.Scrollbar(win2)
        treeScroll.pack(side=RIGHT, fill=Y)
        tree = ttk.Treeview(win2,columns=self.rating_names, show="headings", yscrollcommand = treeScroll)
        rating = []
        for rate_name in self.rating_names:
            rating.append(self.ratings[rate_name].get_rating(reviewer, proposal))
        for col in self.rating_names:
            tree.heading(col, text=col)
        tree.insert('', 'end', iid='line1', values=tuple(rating))

        #tree.heading("1st", text="1st")
        tree.pack(side=LEFT, fill=BOTH)
        treeScroll.config(command=tree.yview)


    def selectItem(self, event):
        # Remove Canvas overlay from GUI
        self._canvas.place_forget()

        # Local Parameters
        x, y, widget = event.x, event.y, event.widget
        item = widget.item(widget.focus())
        #print(item)
        itemText = item['text']
        itemValues = item['values']
        iid = widget.identify_row(y)
        column = event.widget.identify_column(x)
        #print(column)
        #print(column)
        #Leave method if mouse pointer clicks on Treeview area without data
        #if not column or not iid:
        #    return

        #Leave method if selected item's value is empty
        #if not len(itemValues): 
        #    return

        #Get value of selected Treeview cell
        if column == '#0':
            self.cell_value = itemText
        else:
            self.cell_value = itemValues[int(column[1]) - 1]
        #print('column[1] = ',column[1])
        #print('self.cell_value = ',self.cell_value)

        #Leave method if selected Treeview cell is empty
        if not self.cell_value: # date is empty
            print("invalid cell")
            return 
        
        #Get the bounding box of selected cell, a tuple (x, y, w, h), where
        # x, y are coordinates of the upper left corner of that cell relative
        #      to the widget, and
        # w, h are width and height of the cell in pixels.
        # If the item is not visible, the method returns an empty string.
        bbox = widget.bbox(iid, column)
        print('bbox = ', bbox)
        #if not bbox: # item is not visible
        #    return

        # Update and show selection in Canvas Overlay
        self.show_selection(widget, bbox, column)

        print('Selected Cell Value = ', self.cell_value)

        self.do_popup(event, int(column[1:]), self.cell_value)
    
    def show_selection(self, parent, bbox, column):
        """Configure canvas and canvas-textbox for a new selection."""
        #print('@@@@ def show_selection(self, parent, bbox, column):')
        x, y, width, height = bbox
        fudgeTreeColumnx = 19 #Determined by trial & error
        fudgeColumnx = 15     #Determined by trial & error

        # Number of pixels of cell value in horizontal direction
        textw = self._font.measure(self.cell_value)
       # print('textw = ',textw)

        # Make Canvas size to fit selected cell
        self._canvas.configure(width=width, height=height)

        # Position canvas-textbox in Canvas
        #print('self._canvas.coords(self._canvas.text) = ',
              #self._canvas.coords(self._canvas.text))
        if column == '#0':
            self._canvas.coords(self._canvas.text,
                                fudgeTreeColumnx,
                                height/2)
        else:
            self._canvas.coords(self._canvas.text,
                                (width-(textw-fudgeColumnx))/2.0,
                                height/2)

        # Update value of canvas-textbox with the value of the selected cell. 
        self._canvas.itemconfigure(self._canvas.text, text=self.cell_value)

        # Overlay Canvas over Treeview cell
        self._canvas.place(in_=parent, x=x, y=y)

    def proposal_detail(self, event):
        """
        TODO
        """
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
        #self.tree.bind("<Button-3>", self.do_popup)
        #self.tree.bind("<ButtonPress-1>", self.bDown)
        #self.tree.bind("<ButtonRelease-1>",self.bUp)
        #self.tree.bind("<Motion>", self.bMotion)
        #self.tree.bind('<ButtonRelease-1>', self.selectItem)
        self.tree.bind('<Button-3>', self.selectItem)
        self.root.mainloop()

