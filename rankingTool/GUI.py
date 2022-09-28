from .proposal_box import Proposal_Box
from .legend_window import legend_window
from .filter import filter_window
from tkinter import *
from tkinter import ttk
import sys
import numpy as np
import toml

class GUI:
    def __init__(self, rankings, reviewers, reviews, props, configs_path):

        configs = toml.load(configs_path)
        self.name = configs["default"]["name"]
        self.attr_to_rat = configs["graphic_to_rating"]
        self.rat_min = configs["default"]["rat_min"]
        self.rat_max = configs["default"]["rat_max"]
        self.LEN_SHORT_NAME = configs["default"]["num_str"]
        self.default_grap_attr = configs["default_graphic_attributes"]
        self.box_color_dict = configs['box_graph_attributes']["color"]
        self.outline_dict = configs['box_graph_attributes']["outline"]
        self.width_dict = configs['box_graph_attributes']["width"]
        self.dash_dict = configs['box_graph_attributes']["dash"]
        self.box_width = configs["box_size"]["box_width"]
        self.box_height = configs["box_size"]["box_height"]
        self.box_distance_x = configs["box_size"]["box_distance_x"]
        self.box_distance_y = configs["box_size"]["box_distance_y"]
        self.yesno_list = configs["filter"]["yesno_list"]
        self.overall_merit_max = configs["default"]["overall_merit_max"]
        self.overall_merit_min = configs["default"]["overall_merit_min"]

        self.rankings = rankings
        self.reviewers = reviewers
        self.reviews = reviews
        self.props = props

        self.root = Tk()
        self.root.title(self.name)
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
        self.canvas = Canvas(self.root, width=800, height=700, bg="white", yscrollcommand=self.scrlbar2.set, xscrollcommand=self.scrlbar.set,
                        confine=False, scrollregion=(0,0,1000,600))
        self.ties = self.rankings.ties
        self.rate_range = range(self.rat_min, self.rat_max+1)
        self.filter_dict = {}
        self.tied_rect = []
        self.default_filter = {
            "topk": len(self.rankings.columns)
        }
        for rating in self.rankings.get_all_sub_ratings():
            self.filter_dict[rating] = self.rate_range
            self.default_filter[rating] = self.rate_range
        for yesno in self.yesno_list:
            self.default_filter[yesno] = "Yes"
    
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
                    self.canvas.create_rectangle(x0_f-self.box_distance_x*1/3, y0_f-self.box_distance_y*1/3, x1_f+self.box_distance_x*1/3, y1_f+self.box_distance_y*1/3, tag=(f"{reviewer}tie", ))

    def init_number(self):
        self.canvas.create_text(20, 12, text="Merit", font=("Arial", 12))
        for i in range(self.overall_merit_min, self.overall_merit_max+1):
            y0 = self.lines_pos[i-1][1]
            y1 = self.lines_pos[i-1][1]+40
            self.canvas.create_text(15,(y0+y1)//2, text=str(self.overall_merit_max+1-i), font=("Arial", 25))

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
                    self.pos[keys[i], op_dict[keys[i]][rates[j]][k]] = (50+i*self.box_width+i*self.box_distance_x+delta_x, 50+(i+1)*self.box_width+i*self.box_distance_x+delta_x, 
                                2*self.box_height+(self.overall_merit_max-rate)*(self.box_height+self.box_distance_y)*num_most+k*(self.box_height+self.box_distance_y)+(self.overall_merit_max-rate)*self.box_distance_y,
                                3*self.box_height+(self.overall_merit_max-rate)*(self.box_height+self.box_distance_y)*num_most+k*(self.box_height+self.box_distance_y)+(self.overall_merit_max-rate)*self.box_distance_y)
        self.lines_pos = []
        self.ver_lin_pos = []
        for rate in range(self.overall_merit_max-self.overall_merit_min+1):
            self.lines_pos.append((0, self.box_distance_y+self.box_height+rate*(self.box_height+self.box_distance_y)*num_most+rate*self.box_distance_y, len(keys)*270, self.box_distance_y+self.box_height+rate*(self.box_height+self.box_distance_y)*num_most+rate*self.box_distance_y))
            
        for i in range(len(self.columns)):
            self.ver_lin_pos.append((i*self.box_width+50+i*self.box_distance_x, 0, i*self.box_width+50+i*self.box_distance_x, 2200))
            self.ver_lin_pos.append(((i+1)*self.box_width+50+i*self.box_distance_x, 0, (i+1)*self.box_width+50+i*self.box_distance_x, 2200))

    def get_dash(self, reviewer, prop):
        if self.attr_to_rat["Dash"] == "None":
            return self.default_grap_attr["dash"]
        rating = self.rankings.get_sub_rating(self.attr_to_rat["Dash"], reviewer, prop)
        return self.dash_dict[rating]

    def get_outline(self, reviewer, prop):
        if self.attr_to_rat["Outline"] == "None":
            return self.default_grap_attr["outline"]
        rating = self.rankings.get_sub_rating(self.attr_to_rat["Outline"], reviewer, prop)
        return self.outline_dict[rating]

    def get_width(self, reviewer, prop):
        if self.attr_to_rat["Width"] == "None":
            return self.default_grap_attr["width"]
        rating = self.rankings.get_sub_rating(self.attr_to_rat["Width"], reviewer, prop)
        return self.width_dict[rating]
    
    def intial_canvas(self):
        self.get_all_pos()
        self.prop_boxes = []
        for i in range(len(self.columns)):
            box = Proposal_Box(self.canvas, reviewer=self.columns[i], pos=(i*self.box_width+50+i*self.box_distance_x, (i+1)*self.box_width+50+i*self.box_distance_x, 0, self.box_height))
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
        if y <= self.box_height:
            item = self.canvas.find_closest(x, y, halo=2)
            _type = self.canvas.type(item)
            if _type != "rectangle":
                item  = (item[0]-1, )
            tags = self.canvas.gettags(item)
            cur_rev = tags[0]
            index = self.columns.index(cur_rev)
            if index != 0:  
                left_rev = self.columns[index-1]
                self.canvas.move(left_rev, self.box_width+self.box_distance_x, 0)
                self.canvas.move(cur_rev+"text", -(self.box_width+self.box_distance_x), 0)
                self.canvas.move(left_rev+"text", self.box_width+self.box_distance_x, 0)
                self.canvas.move(cur_rev, -(self.box_width+self.box_distance_x), 0)
                self.canvas.move(cur_rev+"tie", -(self.box_width+self.box_distance_x), 0)
                self.canvas.move(left_rev+"tie", self.box_width+self.box_distance_x, 0)
                self.columns[index] = left_rev
                self.columns[index-1] = cur_rev


    def get_box_color(self, reviewer, proposal):
        """
        returns the color of a given proposal box based on its FQ ranking.
        """
        if self.attr_to_rat["Box_Background_Color"] == "None":
            return self.default_grap_attr["color"]
        return self.box_color_dict[self.rankings.get_sub_rating(self.attr_to_rat["Box_Background_Color"],reviewer, proposal)]

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


        self.popup = Menu(self.root, tearoff=0)
        
        self.popup.add_command(label="Filter", command=lambda: self.filter_rect())
        self.popup.add_separator()
        if len(tags) >= 2:
            reviewer = tags[0]
            prop = tags[1]
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
        sub_canvas = Canvas(win2, width=w, height=h, bg="white")
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
                dic = {}         
                for i in range(self.rat_max, self.rat_min-1, -1):
                    dic[i] = f"Vertical Separate Bands Of {i}"
                win3 = Toplevel(self.root)
                win3.title(title)
                win3.geometry('400x300+1400+250')
                w = 400
                h = 300
                x1 = 50
                x2 = 150
                dy = 30
                ini_y = 15
                sub2_canvas = Canvas(win3, width=w, height=h, bg="white")
                for i in range(self.rat_max, self.rat_min-1, -1):
                    sub2_canvas.create_text(x1, (i+1)*dy+ini_y, text=i)
                    sub2_canvas.create_text(x2, (i+1)*dy+ini_y, text=dic[i])
                sub2_canvas.pack()
            else:
                title = grap_attr
                win3 = Toplevel(self.root)
                win3.title(title)
                win3.geometry('400x300')
                w = 400
                h = 300
                x1 = 50
                x2 = 150
                dy = 30
                ini_y = 15
                sub2_canvas = Canvas(win3, width=w, height=h, bg="white")
                fill = {}
                dash = {}
                outline = {}
                width = {}
                for i in range(self.rat_min, self.rat_max+1):
                    fill[str(i)] = None
                    dash[str(i)] = None
                    outline[str(i)] = None
                    width[str(i)] = None
                if grap_attr == "Box_Background_Color":
                    fill = self.box_color_dict
                elif grap_attr == "Dash":
                    dash = self.dash_dict
                elif grap_attr == "Outline":
                    outline = self.outline_dict
                elif grap_attr == "Width":
                    width = self.width_dict
                for i in range(self.rat_max, self.rat_min-1, -1):
                    sub2_canvas.create_text(x1, (i+1)*dy+ini_y, text=i)
                    sub2_canvas.create_rectangle(x2, (i+1)*dy+ini_y, x2+0.4*self.box_width, (i+1)*dy+ini_y+self.box_height, 
                                                fill=fill[str(i)], dash=dash[str(i)], outline=outline[str(i)], width=width[str(i)])
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

    def filter_ratings(self, filter_dict, yesno_dict, topk):
        for rating in filter_dict:
            self.default_filter[rating] = filter_dict[rating]
        for yesno in yesno_dict:
            self.default_filter[yesno] = yesno_dict[yesno]
        self.default_filter["topk"] = topk
        show_rects = self.rankings.updated_pairs(filter_dict, yesno_dict, topk)

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
        dic = {i:self.attr_to_rat[i] for i in self.attr_to_rat if i!="Bands"}
        self.window = legend_window(dic, self, self.rankings.get_all_sub_ratings())
        self.window.show()

    def filter_rect(self):
        self.filter = filter_window(self, self.filter_dict, self.yesno_list, self.rate_range, len(self.rankings.columns),self.default_filter)
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

    def show_width(self, event):
        self.canvas.itemconfigure("event", text="event.width: %s" % event.width)
        self.canvas.itemconfigure("cget", text="winfo_width: %s" % event.widget.winfo_width())


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
        if len(reviews) != 0:
            tree.insert('', 'end', iid='line2', values=tuple(reviews))
        tree.pack(side=LEFT, fill=BOTH)

    def review_text(self, reviewer, proposal_name):
        list_reviews = self.reviews.get_all_review_sub(reviewer, proposal_name)
        self.child_window_review(f"The Review of {proposal_name} by {reviewer}", list_reviews, list_review_titles=self.reviews.review_titles)

    def child_window_review(self, title, list_reviews, list_review_titles):
        win2 = Toplevel(self.root)
        win2.title('Review Details')

        canvas = Canvas(win2, width=500, height=300)
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
            T.insert(END, list_reviews[i])

        canvas.create_window(0, 0, anchor=CENTER, window=container)
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox('all'), 
                        yscrollcommand=scroll.set)
        canvas.pack(fill='both', expand=True, side='left')
        scroll.pack(side=RIGHT, fill=Y, expand=True)

    def set_up(self):
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.show_width)
        self.canvas.bind("<Button-3>", self.do_popup)
        self.canvas.bind("<ButtonRelease-1>",self.ret_colors)
        self.canvas.bind('<Double-1>', self.swap_left) 
        self.canvas.bind('<ButtonPress-1>', self.selectItem)

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
