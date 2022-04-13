import tkinter as tk
from tkinter import ttk
from Ranking import Ranking

def bDown(event):
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
        visual_drag.configure(displaycolumns=[col_from_id])
        visual_drag.place(in_=tv, x=bbox[0], y=0, anchor='nw', width=bbox[2], relheight=1)
    else:
        col_from = None

def bUp(event):
    tv = event.widget
    col_to = int(tv.identify_column(event.x)[1:]) - 1  # subtract 1 because display columns array 0 = tree column 1
    visual_drag.place_forget()
    if col_from is not None:
        tv.heading(col_from_id, text=visual_drag.heading('#1', 'text'))
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

def bMotion(event):
    # drag around label if visible
    if visual_drag.winfo_ismapped():
        visual_drag.place_configure(x=dx + event.x)
    

ranking_path = input("Please Enter The Name of the Ranking File: ")
rankings = Ranking(ranking_path)
vertical_rankings = rankings.get_vertical_rankings()

# Variable to hold initial choice of column to move
col_from = 0

root = tk.Tk()
root.title('Rankings UI')
root.geometry('800x500')
#root['bg'] = '#AC99F2'

# Set Scroll Bar
scrlbar2 = ttk.Scrollbar(root)
scrlbar2.pack(side="right", fill="y")

scrlbar = ttk.Scrollbar(root,orient ='horizontal')
scrlbar.pack(side="bottom", fill="x")

# List of columns
columns = rankings.get_columns()

# Create treeview with columns. Display all columns
tree = ttk.Treeview(root,yscrollcommand=scrlbar2.set, height = 33, columns=columns, xscrollcommand=scrlbar.set, show='headings')

# treeview to show column motion
visual_drag = ttk.Treeview(root, yscrollcommand=scrlbar2.set, height = 33, columns=columns, xscrollcommand=scrlbar.set, show='headings')
tree.pack()

scrlbar2.config(command=tree.yview)
scrlbar.config(command=tree.xview)

# Set headers
for col in columns:
    tree.heading(col, text=col)
    visual_drag.heading(col, text=col)

nums_rows = rankings.get_num_rows()
# insert some items into the tree
for i in range(nums_rows):
    tree.insert('', 'end', iid='line%i' % i,
                values=tuple(vertical_rankings[i]))
    visual_drag.insert('', 'end', iid='line%i' % i,
                       values=tuple(vertical_rankings[i]))

#tree.grid()
tree.bind("<ButtonPress-1>", bDown)
tree.bind("<ButtonRelease-1>",bUp)
tree.bind("<Motion>",bMotion)

root.mainloop()

