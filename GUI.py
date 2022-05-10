  
from tkinter import *
from tkinter import ttk
import tkinter as tk
import sys

import numpy as np
from Proposal import proposal
from Ranking import rankings
from Review import review
from Proposal_Box import Proposal_Box

BOX_COLOR_DICT = {
    5 : "white",
    4 : "wheat1",
    3 : "wheat2",
    2 : "wheat3",
    1 : "wheat4",
}

OUTLINE_DICT = {
    5 : "blue",
    4 : "red",
    3 : "purple",
    2 : "grey",
    1 : "black",
}

DELTA_X = 0
BOX_WIDTH = 200
BOX_HEIGHT = 20
BOX_DISTANCE_X = 50
BOX_DISTANCE_Y = 10

X_COOR_DICT = {
    5 : 2*DELTA_X,
    4 : DELTA_X,
    1 : -2*DELTA_X,
    2 : -DELTA_X,
    3 : 0,
    0 : 0
}

WIDTH_DICT = {
    5: 7,
    4: 5,
    3: 3,
    2: 1,
    1: 0
}

DASH_DICT = {
    5: (),
    4: (5),
    3: (50, 50, 2),
    2: (30,10, 2, 1),
    1: (255,255, 20, 255,255)
}



class GUI:
    def __init__(self, ranking_path, reviews_path, ratings_paths, proposals_path, rating_to_attr) -> None:
        self.rat_to_attr = rating_to_attr
        self.attr_to_dict = {
            "Bands": None,
            "Box_Background_Color": BOX_COLOR_DICT,
            "Width": WIDTH_DICT,
            "Dash": DASH_DICT,
            "Outline" : OUTLINE_DICT
        }
        self.rankings = rankings(ranking_path, ratings_paths)
        self.reviews = review(reviews_path)
        self.props: proposal() = None   # Not Implemented Yet.

        self.root = Tk()
        self.root.title('Rankings UI')
        self.root.geometry('800x700')
        self.root['bg'] = '#AC99F2' # Background Color of the entire UI

        # Set Scroll Bar
        self.scrlbar2 = ttk.Scrollbar(self.root)
        self.scrlbar2.pack(side="right", fill="y")

        self.scrlbar = ttk.Scrollbar(self.root, orient ='horizontal')
        self.scrlbar.pack(side="bottom", fill="x")

        self.columns = self.rankings.get_columns()
        self.overall_rankings = self.rankings.get_all_rankings()
        self.canvas = tk.Canvas(self.root, width=800, height=700, bg="white", yscrollcommand=self.scrlbar2.set, xscrollcommand=self.scrlbar.set,
                        confine=False, scrollregion=(0,0,1000,600))

        self.intial_canvas()
        self.init_number()

        self.scrlbar2.config(command=self.canvas.yview)
        self.scrlbar.config(command=self.canvas.xview)
        self.canvas.pack()


        self.set_up()

    def init_number(self):
        self.canvas.create_text(20, 12, text="Merit", font=("Arial", 12))
        for i in range(1, 6):
            y0 = self.lines_pos[i-1][1]
            y1 = self.lines_pos[i-1][1]+40
            #self.canvas.create_rectangle(x0, y0, x1, y1)
            self.canvas.create_text(15,(y0+y1)//2, text=str(6-i), font=("Arial", 25))
            #l = Label(self.canvas,text=str(6-i),)
            #l.place(x=0, y=self.lines_pos[i-1][1])
            #l.config(yscrollcommand=self.scrlbar2.set)

    def get_all_pos(self):
        op_dict, num_most = self.rankings.get_op_rankings()
        self.pos = {}
        keys = list(op_dict.keys())
        for i in range(len(keys)):
            rates = list(op_dict[keys[i]].keys())
            for j in range(len(rates)):
                rate = rates[j]
                for k in range(len(op_dict[keys[i]][rates[j]])):
                    # For dx graphical attributes
                    #x_coord_rat = self.rankings.get_sub_rating(self.rat_to_attr["X_coord"], keys[i], op_dict[keys[i]][rates[j]][k])
                    #delta_x = self.get_delta_x(x_coord_rat)
                    delta_x = 0
                    self.pos[keys[i], op_dict[keys[i]][rates[j]][k]] = (50+i*BOX_WIDTH+i*BOX_DISTANCE_X+delta_x, 50+(i+1)*BOX_WIDTH+i*BOX_DISTANCE_X+delta_x, 
                                2*BOX_HEIGHT+(5-rate)*(BOX_HEIGHT+BOX_DISTANCE_Y)*num_most+k*(BOX_HEIGHT+BOX_DISTANCE_Y)+(5-rate)*BOX_DISTANCE_Y,
                                3*BOX_HEIGHT+(5-rate)*(BOX_HEIGHT+BOX_DISTANCE_Y)*num_most+k*(BOX_HEIGHT+BOX_DISTANCE_Y)+(5-rate)*BOX_DISTANCE_Y)
        self.lines_pos = []
        self.ver_lin_pos = []
        for rate in range(5):
            self.lines_pos.append((0, BOX_DISTANCE_Y+BOX_HEIGHT+rate*(BOX_HEIGHT+BOX_DISTANCE_Y)*num_most+rate*BOX_DISTANCE_Y, 2200, BOX_DISTANCE_Y+BOX_HEIGHT+rate*(BOX_HEIGHT+BOX_DISTANCE_Y)*num_most+rate*BOX_DISTANCE_Y))
            
        for i in range(len(self.columns)):
            self.ver_lin_pos.append((i*BOX_WIDTH+50+i*BOX_DISTANCE_X, 0, i*BOX_WIDTH+50+i*BOX_DISTANCE_X, 2200))
            self.ver_lin_pos.append(((i+1)*BOX_WIDTH+50+i*BOX_DISTANCE_X, 0, (i+1)*BOX_WIDTH+50+i*BOX_DISTANCE_X, 2200))

    def get_delta_x(self, rating):
        return X_COOR_DICT[rating]

    def get_dash(self, reviewer, prop):
        rating = self.rankings.get_sub_rating(self.rat_to_attr["Dash"], reviewer, prop)
        return DASH_DICT[rating]

    def get_outline(self, reviewer, prop):
        rating = self.rankings.get_sub_rating(self.rat_to_attr["Outline"], reviewer, prop)
        return OUTLINE_DICT[rating]

    def get_width(self, reviewer, prop):
        rating = self.rankings.get_sub_rating(self.rat_to_attr["Width"], reviewer, prop)
        return WIDTH_DICT[rating]
    
    def intial_canvas(self):
        self.get_all_pos()
        for i in range(len(self.columns)):
            box = Proposal_Box(self.canvas, reviewer=self.columns[i], pos=(i*BOX_WIDTH+50+i*BOX_DISTANCE_X, (i+1)*BOX_WIDTH+50+i*BOX_DISTANCE_X, 0, BOX_HEIGHT))
        for pair in self.pos.keys():   
            color = self.get_box_color(pair[0], pair[1])
            dash = self.get_dash(pair[0], pair[1])
            outline = self.get_outline(pair[0], pair[1])
            width = self.get_width(pair[0], pair[1])
            box = Proposal_Box(self.canvas, pair[0], self.pos[pair], pair[1], color, dash, outline, width)
        for line in self.lines_pos:
            self.canvas.create_line(line[0], line[1], line[2], line[3], width=1.5, fill="gray")
        #for ver_line in self.ver_lin_pos:
            #self.canvas.create_line(ver_line[0], ver_line[1], ver_line[2], ver_line[3], width=1, fill="skyblue3", dash=(1,2))


    def selectItem(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(x, y)

        _type = self.canvas.type(item)
        if _type != "rectangle":
            item  = (item[0]-1, )
        tags = self.canvas.gettags(item)
        if len(tags) >= 2 and tags[1] != "current":
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
            self.canvas.move(left_rev, BOX_WIDTH+BOX_DISTANCE_X, 0)
            self.canvas.move(cur_rev+"text", -(BOX_WIDTH+BOX_DISTANCE_X), 0)
            self.canvas.move(left_rev+"text", BOX_WIDTH+BOX_DISTANCE_X, 0)
            self.canvas.move(cur_rev, -(BOX_WIDTH+BOX_DISTANCE_X), 0)

            self.columns[index] = left_rev
            self.columns[index-1] = cur_rev


    def get_box_color(self, reviewer, proposal):
        """
        returns the color of a given proposal box based on its FQ ranking.
        """
        return BOX_COLOR_DICT[self.rankings.get_sub_rating(self.rat_to_attr["Box_Background_Color"],reviewer, proposal)]
        

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

        self.popup = Menu(self.root, tearoff=0)
        
        self.popup.add_command(label="Legends", command=lambda: self.legend_sub())
        
        self.popup.add_separator()
        self.popup.add_command(label="Rating Details", command=lambda: self.rating_detail(reviewer, prop))
        self.popup.add_command(label="Review Text", command=lambda: self.review_text(reviewer, prop))
        self.popup.add_command(label="Proposal Details", command=lambda: self.proposal_detail(prop))


        self.popup.add_separator()
        self.popup.add_command(label="Exit", command=lambda: self.closeWindow())
        try:
            self.popup.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup.grab_release()

    def legend_sub(self):
        win2 = Toplevel()
        win2.title('Legends')
        win2.geometry('400x300')
        w = 400
        h = 300
        x1 = 100
        x2 = 300
        dy = 30
        ini_y = 50
        sub_canvas = tk.Canvas(win2, width=w, height=h, bg="white")
        keys = list(self.rat_to_attr.keys())
        sub_canvas.create_text(x1, ini_y, text="Graphical Attributes", font=("bold", 13))
        sub_canvas.create_text(x2, ini_y, text="Ratings", font=("bold", 13))
        for i in range(len(keys)):
            sub_canvas.create_text(x1, (i+1)*dy+ini_y, text=keys[i], tags=(f"{keys[i]}"))
            sub_canvas.create_text(x2, (i+1)*dy+ini_y, text=self.rat_to_attr[keys[i]], tags=(f"{keys[i]}"))
        sub_canvas.pack()


        def legend_subsub(event):
            x = sub_canvas.canvasx(event.x)
            y = sub_canvas.canvasy(event.y)
            item = sub_canvas.find_closest(x, y)
            grap_attr = sub_canvas.gettags(item)[0]
            if grap_attr == "Bands":
                title = grap_attr
                dic = {
                    5: "Vertical Separate Bands Of 5",
                    4: "Vertical Separate Bands Of 4",
                    3: "Vertical Separate Bands Of 3",
                    2: "Vertical Separate Bands Of 2",
                    1: "Vertical Separate Bands Of 1",
                }
                win3 = Toplevel()
                win3.title(title)
                win3.geometry('400x300')
                w = 400
                h = 300
                x1 = 50
                x2 = 150
                dy = 30
                ini_y = 15
                sub2_canvas = tk.Canvas(win3, width=w, height=h, bg="white")
                for i in range(5, 0, -1):
                    sub2_canvas.create_text(x1, (i+1)*dy+ini_y, text=i)
                    sub2_canvas.create_text(x2, (i+1)*dy+ini_y, text=dic[i])
                sub2_canvas.pack()
            else:
                title = grap_attr
                dic = self.attr_to_dict[grap_attr]
                win3 = Toplevel()
                win3.title(title)
                win3.geometry('400x300')
                w = 400
                h = 300
                x1 = 50
                x2 = 150
                dy = 30
                ini_y = 15
                sub2_canvas = tk.Canvas(win3, width=w, height=h, bg="white")
                fill = {
                    5: None,
                    4: None,
                    3: None,
                    2: None,
                    1: None
                }
                dash =  {
                    5: None,
                    4: None,
                    3: None,
                    2: None,
                    1: None
                }
                outline =  {
                    5: None,
                    4: None,
                    3: None,
                    2: None,
                    1: None
                }
                width =  {
                    5: None,
                    4: None,
                    3: None,
                    2: None,
                    1: None
                }
                if grap_attr == "Box_Background_Color":
                    fill = dic
                elif grap_attr == "Dash":
                    dash = dic
                elif grap_attr == "Outline":
                    outline = dic
                elif grap_attr == "Width":
                    width = dic
                for i in range(5, 0, -1):
                    sub2_canvas.create_text(x1, (i+1)*dy+ini_y, text=i)
                    sub2_canvas.create_rectangle(x2, (i+1)*dy+ini_y, x2+0.4*BOX_WIDTH, (i+1)*dy+ini_y+BOX_HEIGHT, 
                                                fill=fill[i], dash=dash[i], outline=outline[i], width=width[i])
                    #sub2_canvas.create_text(x2, (i+1)*dy+ini_y, text=dic[i])
                sub2_canvas.pack()
        sub_canvas.bind('<Double-1>', legend_subsub) 








    def rating_detail(self, reviewer, prop):
        self.child_window_ratings("Rating Details", reviewer, prop)


    def proposal_detail(self, prop):
        if self.props is None:
            text = "No Information Now."
        else:
            text = self.props.get_detail(prop)
        self.child_window_prop(f"Details of {prop}", text)

    def child_window_prop(self, title, text):
        win2 = Toplevel()
        win2.title('Proposal Details')
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
        win2.title('Ratings Details')
        Label(win2, text=name).pack()
        treeScroll = ttk.Scrollbar(win2)
        treeScroll.pack(side=RIGHT, fill=Y)
        col_names = self.rankings.get_all_sub_ratings()
        tree = ttk.Treeview(win2,columns=col_names, show="headings", yscrollcommand = treeScroll)
        rating = []
        for rate_name in col_names:
            rating.append(self.rankings.get_sub_rating(rate_name, reviewer, proposal))
        for col in col_names:
            tree.heading(col, text=col)
        tree.insert('', 'end', iid='line1', values=tuple(rating))
        tree.pack(side=LEFT, fill=BOTH)
        treeScroll.config(command=tree.yview)


    def review_text(self, reviewer, proposal_name):
        text = self.reviews.get_review(reviewer, proposal_name)
        self.child_window_text(f"The Review of {proposal_name} by {reviewer}", text)

    def child_window_text(self, title, text):
        win2 = Toplevel()
        win2.title('Review Details')
        T = Text(win2, height=20, width=52)
        # Create label
        l = Label(win2, text=title)
        l.pack()
        T.pack()
        l.config(font =("Times", "24", "bold"))
        T.config(font =("Times", "16"))
        T.insert(tk.END, text)


    def set_up(self):
        self.canvas.bind("<Button-2>", self.do_popup)
        self.canvas.bind("<ButtonRelease-1>",self.ret_colors)
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
        if len(tags) >= 2 and tags[1] != "current":
            prop = tags[1]
            all_items = self.canvas.find_withtag(prop)
            for item in all_items:
                reviewer = self.canvas.gettags(item)[0]
                self.canvas.itemconfig(item, fill=self.get_box_color(reviewer, prop))


    def show(self):
        self.root.mainloop()
