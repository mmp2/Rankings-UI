from tkinter import *
from tkinter import ttk
import tkinter as tk
import sys
import numpy as np
from Proposal_Box import Proposal_Box
from start_window import legend_window
from filter import filter_window
import toml

configs = toml.load("config_rest.toml")
NAME = configs["default"]["name"]
ATTR_TO_RAT = configs["graphic_to_rating"]
LEN_SHORT_NAME = configs["default"]["num_str"]
DEFAULT_GRAP_ATTR = configs["default_graphic_attributes"]
BOX_COLOR_DICT = configs['box_graph_attributes']["color"]
OUTLINE_DICT = configs['box_graph_attributes']["outline"]
WIDTH_DICT = configs['box_graph_attributes']["width"]
DASH_DICT = configs['box_graph_attributes']["dash"]
BOX_WIDTH = configs["box_size"]["box_width"]
BOX_HEIGHT = configs["box_size"]["box_height"]
BOX_DISTANCE_X = configs["box_size"]["box_distance_x"]
BOX_DISTANCE_Y = configs["box_size"]["box_distance_y"]
LIST_REVIEW_TITLES = configs["review"]["titles"]

class GUI:
    def __init__(self, rankings, reviewers, reviews, props, attr_to_rat=ATTR_TO_RAT):
        """
        rankings, reviewers, reviews, props: Similar classes that contains all specific functional methods as in examples.
        attr_to_rat: A dictionary that contains the relationship between each graphical attribute to a rating.
        """
        self.attr_to_rat = attr_to_rat

        self.rankings = rankings
        self.reviewers = reviewers
        self.reviews = reviews
        self.props = props

        self.root = Tk()
        self.root.title(NAME)
        screen_height = self.root.winfo_screenheight()
        y = int(round((screen_height/2) - (700/2)))
        self.root.geometry(f'800x700+100+{str(y)}')
        self.root['bg'] = '#AC99F2' # Background Color of the entire UI
        s = ttk.Style()
        s.theme_use('clam')

        # Set Scroll Bar
        self.scrlbar2 = ttk.Scrollbar(self.root)
        self.scrlbar2.pack(side="right", fill="y")
        self.scrlbar = ttk.Scrollbar(self.root, orient ='horizontal')
        self.scrlbar.pack(side="bottom", fill="x")

        self.columns = self.rankings.get_columns()
        self.canvas = tk.Canvas(self.root, width=800, height=700, bg="white", yscrollcommand=self.scrlbar2.set, xscrollcommand=self.scrlbar.set,
                        confine=False, scrollregion=(0,0,1000,600))
        self.ties = self.rankings.ties
        self.rate_range = range(0, 6)
        self.filter_dict = {}
        for rating in self.rankings.get_all_sub_ratings():
            self.filter_dict[rating] = self.rate_range
        self.intial_canvas()
        self.init_number()
        self.init_tied_rect()
        self.scrlbar2.config(command=self.canvas.yview)
        self.scrlbar.config(command=self.canvas.xview)
        self.canvas.pack()
        self.set_up()

    def init_tied_rect(self):
        if self.ties is not None:
            for reviewer in self.ties.keys():
                for tie in self.ties[reviewer]:
                    y0_f = np.inf
                    y1_f = -np.inf
                    x0_f = 0
                    x1_f = 0
                    for paper in tie:
                        x0_f, x1_f, y0, y1 = self.pos[(reviewer, paper)]
                        if y0 < y0_f:
                            y0_f = y0
                        if y1 > y1_f:
                            y1_f = y1
                    self.canvas.create_rectangle(x0_f-BOX_DISTANCE_X*1/3, y0_f-BOX_DISTANCE_Y*1/3, x1_f+BOX_DISTANCE_X*1/3, y1_f+BOX_DISTANCE_Y*1/3)

    def init_number(self):
        self.canvas.create_text(20, 12, text="Merit", font=("Arial", 12))
        for i in range(1, 6):
            y0 = self.lines_pos[i-1][1]
            y1 = self.lines_pos[i-1][1]+40
            self.canvas.create_text(15,(y0+y1)//2, text=str(6-i), font=("Arial", 25))

    def get_all_pos(self):
        op_dict, num_most = self.rankings.get_op_rankings()
        self.pos = {}
        keys = list(op_dict.keys())
        for i in range(len(keys)):
            rates = list(op_dict[keys[i]].keys())
            for j in range(len(rates)):
                rate = int(rates[j])
                for k in range(len(op_dict[keys[i]][rates[j]])):
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

    def get_dash(self, reviewer, prop):
        if self.attr_to_rat["Dash"] == "None":
            return DEFAULT_GRAP_ATTR["dash"]
        rating = self.rankings.get_sub_rating(self.attr_to_rat["Dash"], reviewer, prop)
        return DASH_DICT[rating]

    def get_outline(self, reviewer, prop):
        if self.attr_to_rat["Outline"] == "None":
            return DEFAULT_GRAP_ATTR["outline"]
        rating = self.rankings.get_sub_rating(self.attr_to_rat["Outline"], reviewer, prop)
        return OUTLINE_DICT[rating]

    def get_width(self, reviewer, prop):
        if self.attr_to_rat["Width"] == "None":
            return DEFAULT_GRAP_ATTR["width"]
        rating = self.rankings.get_sub_rating(self.attr_to_rat["Width"], reviewer, prop)
        return WIDTH_DICT[rating]
    
    def intial_canvas(self):
        self.get_all_pos()
        self.prop_boxes = []
        for i in range(len(self.columns)):
            box = Proposal_Box(self.canvas, reviewer=self.columns[i], pos=(i*BOX_WIDTH+50+i*BOX_DISTANCE_X, (i+1)*BOX_WIDTH+50+i*BOX_DISTANCE_X, 0, BOX_HEIGHT))
        for pair in self.pos.keys():   
            color = self.get_box_color(pair[0], pair[1])
            dash = self.get_dash(pair[0], pair[1])
            outline = self.get_outline(pair[0], pair[1])
            width = self.get_width(pair[0], pair[1])
            box = Proposal_Box(self.canvas, pair[0], self.pos[pair], pair[1], color, dash, outline, width)
            self.prop_boxes.append(box)
        for line in self.lines_pos:
            self.canvas.create_line(line[0], line[1], line[2], line[3], width=1.5, fill="gray")

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
        if y <= BOX_HEIGHT:
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
        if self.attr_to_rat["Box_Background_Color"] == "None":
            return DEFAULT_GRAP_ATTR["color"]
        return BOX_COLOR_DICT[self.rankings.get_sub_rating(self.attr_to_rat["Box_Background_Color"],reviewer, proposal)]

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
        
        #self.popup.add_command(label="Legends", command=lambda: self.legend_sub())
        
        self.popup.add_command(label="Filter", command=lambda: self.filter_rect())
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
        win2 = Toplevel(self.root)
        win2.title('Legends')
        win2.geometry('400x300+1000+250')
        w = 400
        h = 300
        x1 = 100
        x2 = 300
        dy = 30
        ini_y = 50
        sub_canvas = tk.Canvas(win2, width=w, height=h, bg="white")
        keys = list(self.attr_to_rat.keys())
        sub_canvas.create_text(x1, ini_y, text="Graphical Attributes", font=("bold", 13))
        sub_canvas.create_text(x2, ini_y, text="Ratings", font=("bold", 13))
        for i in range(len(keys)):
            sub_canvas.create_text(x1, (i+1)*dy+ini_y, text=keys[i], tags=(f"{keys[i]}"))
            sub_canvas.create_text(x2, (i+1)*dy+ini_y, text=self.attr_to_rat[keys[i]], tags=(f"{keys[i]}"))
        change_button = Button(win2, text="Change Graphical Attributes",  command=self.change_attribute)
        change_button.pack()
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
                win3 = Toplevel(self.root)
                win3.title(title)
                win3.geometry('400x300+1400+250')
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
                win3 = Toplevel(self.root)
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

    def update_all_rects(self, res):
        self.attr_to_rat = res
        for box in self.prop_boxes:
            reviewer, prop = box.get_reviewer_prop()
            color = self.get_box_color(reviewer, prop)
            dash = self.get_dash(reviewer, prop)
            outline = self.get_outline(reviewer, prop)
            width = self.get_width(reviewer, prop)
            box.update_rect(color, dash, outline, width)

    def filter_ratings(self, filter_dict, repo, topk):
        self.filter_dict = filter_dict
        show_rects = self.rankings.updated_pairs(filter_dict, repo, topk)
        for box in self.prop_boxes:
            reviewer, prop = box.get_reviewer_prop()
            state = "hidden"
            for i in range(len(show_rects)):
                if show_rects[i][0] == reviewer and show_rects[i][1] == prop:
                    state = "normal"
                    break
            box.update_rect(state=state)
            box.update_text(state=state)

    def change_attribute(self):
        self.window = legend_window(self.attr_to_rat, self)
        self.window.show()
        #self.attr_to_rat = self.window.get_pair()
        #self.update_all_rects()

    def filter_rect(self):
        #if self.filter_dict == N
        self.filter = filter_window(self, self.filter_dict, self.rate_range, len(self.rankings.columns))
        self.filter.show()

    def rating_detail(self, reviewer, prop):
        self.child_window_ratings("Rating Details", reviewer, prop)

    def proposal_detail(self, prop):
        text = self.props.get_detail(prop)
        self.child_window_prop(f"Details of {prop}", text)

    def child_window_prop(self, title, text):
        win3 = Toplevel(self.root)
        win3.title('Proposal Details')
        T = Text(win3, height=20, width=52)
        T.insert("1.0", text)
        # Create label
        l = Label(win3, text=title)
        l.pack()
        T.pack()
        l.config(font =("Times", "24", "bold"))
        T.config(font =("Times", "16"))



    def child_window_ratings(self, name, reviewer, proposal):
        win2 = Toplevel(self.root)
        win2.geometry('1000x300')
        win2.title('Ratings Details')
        Label(win2, text=name).pack()

        col_names = self.rankings.get_all_sub_ratings()
    
        s = ttk.Style()
        s.theme_use('clam')

        # Add the rowheight

        s.configure('Treeview', rowheight=100)
        tree = ttk.Treeview(win2, columns=col_names, selectmode="extended", show="headings")
        treeScroll = ttk.Scrollbar(win2, orient="horizontal", command=tree.xview)
        treeScroll.pack(side=BOTTOM, fill=X)
        tree.configure(xscrollcommand=treeScroll.set)
        rating = []
        reviews = self.reviews.get_reviews_in_order(reviewer, proposal, col_names)
        for rate_name in col_names:
            rating.append(self.rankings.get_sub_rating(rate_name, reviewer, proposal))
            tree.heading(rate_name, text=rate_name)
        tree.insert('', 'end', iid='line1', values=tuple(rating))
        tree.insert('', 'end', iid='line2', values=tuple(reviews))
        tree.pack(side=LEFT, fill=BOTH)

    def review_text(self, reviewer, proposal_name):
        list_reviews = self.reviews.get_all_review_sub(reviewer, proposal_name)
        self.child_window_review(f"The Review of {proposal_name} by {reviewer}", list_reviews, list_review_titles=LIST_REVIEW_TITLES)

    def child_window_review(self, title, list_reviews, list_review_titles):
        win2 = Toplevel(self.root)
        win2.title('Review Details')

        canvas = tk.Canvas(win2, width=500, height=300)
        container = ttk.Frame(canvas)
        scroll = ttk.Scrollbar(win2, orient="vertical", command=canvas.yview)
        
        l = Label(container, text=title)
        l.pack()
        l.config(font =("Times", "18", "bold"))
        for i in range(len(list_reviews)):
            T = Text(container, height=8, width=52, font =("Times", "12"))
            L = Label(container, text=list_review_titles[i], font=("Times", "16", "bold"))
            L.pack()
            T.pack()
            T.insert(tk.END, list_reviews[i])

        canvas.create_window(0, 0, anchor=tk.CENTER, window=container)
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox('all'), 
                        yscrollcommand=scroll.set)
        canvas.pack(fill='both', expand=True, side='left')
        scroll.pack(side=RIGHT, fill=Y, expand=True)

    def set_up(self):
        self.canvas.bind("<Button-3>", self.do_popup)
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
        self.legend_sub()
        self.root.mainloop()
