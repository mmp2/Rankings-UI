import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import PIL.Image
import PIL.ImageTk
import numpy as np

from .java_import import java_import
import json

class census_window:
    """
        A class to represent the window of concensus ranking.

        ...
        Attributes
        ----------
        root (Tk):
            Root of the window.
        GUI (GUI):
            From class GUI.
        rankings_name (dict):
            A dictionary of item names.
            rankings_name['long'] is a longer version and
            rankings_name['short'] is a shorter version.
        ratings (df):
            DataFrame of the overall ratings (columns represent proposals). Default is None.
        rankings (df):
            DataFrame of the overall rankings (columns represent proposals). Default is None.

        Methods
        -------
        show():
            Show the consensus rankings window.
        write_data_txt():
            Write the rankings/ratings data to a .txt file for packages to run.
        hide():
            Hide the consensus rankings window temporarily.
        reshow():
            Reopen the consensus rankings window.
        ranking_model():
            Region for computing the models.
        option_changed():
            Resets parameters when the model option is changed.
        create_wigets2():
            Create wigets for choosing the parameters.
        consensus_ranking():
            Compute the model selected.
        borda_type():
            Depending on the type of data we have, change borda paths.
        display_borda(ranking):
            Display borda results.
        display_rankings(model_name, rankings):
            Display results for Mallows, GMM, Landmarks.
        display_rim():
            Display results for RIM.
        combine_results():
            Organize model results to self.results.
        get_cen_rankings():
            Returns the most recent consensus rankings computed.
        get_ranking_pos(rankings):
            Compute coordinates for the rankings.
        set_working_directory():
            Set working directory.
        reloadmodel():
            Reload the model from .toml file.
        save_model():
            Save the current results to a .json file.
        generate_bootstrap(nBoot, model):
            Generate bootstrap samples and compute the results.
    """
    def __init__(self, root, GUI, rankings_name, ratings=None, rankings=None) -> None:
        """
            Initialize the concensus ranking window (canvas, scrollbar, ...)
        """
        self.rankings_names = rankings_name
        self.gui = GUI
        self.gui.results = {}
        self.type = "Both"
        if rankings is None:
            self.type = "Rate"
        if ratings is None:
            self.type = "Rank"
        self.ratings = ratings
        self.rankings = rankings
        self.model_attr = {'Mallows': dict(),
                           'RIM': dict(iters=100, temp=.03),
                           'GMM': dict(),
                           'Landmarks': dict(),
                           'Borda': dict()}

        self.root3 = Toplevel(root)
        self.root3.title('Display Concensus Rankings')
        self.root3.geometry('1200x700+200+250')
        self.root3['bg'] = '#AC99F2'
        self.model_xpart = 3
        self.box_width = 120
        self.box_height = 25
        self.button_yshift = 30
        self.model_order = []
        self.label_entry = [[] for _ in range(len(self.model_attr))]
        self.results = {}
        self.para_dict_list = {}
        self.Scroll = ttk.Scrollbar(self.root3, orient='horizontal')
        self.Scroll.pack(side="bottom", fill="x", expand=False)
        self.Scroll2 = ttk.Scrollbar(self.root3, orient='vertical')
        self.Scroll2.pack(side="right", fill="y", expand=False)
        self.canvas2 = Canvas(self.root3, width=1200, height=700, xscrollcommand=self.Scroll.set, scrollregion=(0, 0, 2500,1000))
        self.root3.grid_rowconfigure(0, weight=1)
        self.root3.grid_columnconfigure(0, weight=1)
        self.canvas2.pack(fill='both', side='left',expand=True)
        self.Scroll.config(command=self.canvas2.xview)
        self.Scroll2.config(command=self.canvas2.yview)
        self.canvas2.grid_rowconfigure(7, minsize=25)
        self.image = []
        self.treeplot = []
        self.directory = StringVar()
        #self.directory.set("/Users/xuliu/Library/CloudStorage/OneDrive-UW/Rankings-UI-main/Restaurants_Example")

        s = ttk.Style()
        s.theme_use('clam')

        label = Label(self.canvas2, text="Choose model for consensus ranking:",font=('Comic Sans MS', 15),takefocus=0)
        self.canvas2.create_window((20, 20), window=label, anchor=W)


    def show(self):
        """
            Display the oncensus rankings window.
        """
        self.ranking_model()
        self.root3.mainloop()

    def write_data_txt(self):
        """
            Write txt file(s) for packages to run.
        """
        if self.rankings is not None:
            self.rankings_path = self.directory.get() + "/rankings.txt"
            self.rankings.to_csv(self.rankings_path, header=None, index=None, sep=' ',mode="w")

        if self.ratings is not None:
            self.ratings_path = self.directory.get() + "/ratings.txt"
            self.ratings.to_csv(self.ratings_path, header=None, index=None, sep=' ',mode="w")


    def hide(self):
        """
            Hide consensus ranking window temporarily.
        """
        self.root3.withdraw()

    def reshow(self):
        """
            Reshow consensus ranking window.
        """
        self.root3.deiconify()

    def ranking_model(self):
        """
            Model computation panel with the following buttons:
            Button "Set working directory": set working directory;
            Button "Load Ranking Data": load data file (row represents each participant);
            Button "Load Ranking Model Results": load model results (.json file);
            Button "Compute Consensus Ranking": compute selected model ranking results;
            Button "Reset parameter(s)": reset parameters to their default values;
            Button "Save Models": save model results to a .json file.
        """
       # Selecting model for computing consensus ranking
        options_list = list(self.model_attr.keys())
        if self.type == "Rank":
            options_list.remove("Landmarks")
        elif self.type == "Rate":
            options_list = ["Landmarks","Borda"]

        #options_list.remove("Landmarks")
        self.model_choice = StringVar(self.canvas2)
        self.model_choice.set(options_list[0])
        model_name = self.model_choice.get()
        self.modelvarq = self.model_attr[model_name]
        self.para_list = []
        self.label = []
        self.para_entry = []
       #Load in parameters
        for i in range(len(self.modelvarq)):
            tkvarq = StringVar(self.canvas2)
            self.para_list.append(tkvarq)
            self.para_wigets = self.create_wigets2(self.para_list[i], i)
        self.model_choice.trace("w", lambda *args: self.option_changed())
        self.model_menu = OptionMenu(self.canvas2, self.model_choice, *options_list)
        self.canvas2.create_window((280, 20), window=self.model_menu, anchor=W)

        #Other buttons for loading data and compute rankings
        self.rankings_path = StringVar(self.canvas2)
        self.models_path = StringVar(self.canvas2)
        setdirectory_button = Button(self.canvas2, text="Set working directory", command=self.set_working_directory)
        self.canvas2.create_window((20, self.button_yshift + 20), window=setdirectory_button, anchor=W)
        loadmodel_button = Button(self.canvas2, text="Load Model Results", command=self.reloadmodel)
        self.canvas2.create_window((20, 2*self.button_yshift + 20), window=loadmodel_button, anchor=W)
        consensus_button = Button(self.canvas2, text="Compute Consensus Ranking", command=self.consensus_ranking)
        self.canvas2.create_window((20, 3*self.button_yshift + 20), window=consensus_button, anchor=W)
        reset_button = Button(self.canvas2, text="Reset parameter(s)", command=self.option_changed, bg="sky blue",takefocus=0)
        self.canvas2.create_window((20, 4*self.button_yshift + 20), window=reset_button, anchor=W)
        savemodel_button = Button(self.canvas2, text="Save Models", command=self.save_model)
        self.canvas2.create_window((20, 5*self.button_yshift + 20), window=savemodel_button, anchor=W)

        #lines on canvas
        self.canvas2.update()
        self.yshift = 230
        self.canvas2.create_line(0, self.yshift, 2500, self.yshift, width=1.5, fill="gray85")
        self.canvas2.create_line(480, self.yshift, 480, 1000, width=1.5, fill="gray85")
        self.canvas2.create_line(480*2, self.yshift, 480*2, 1000, width=1.5, fill="gray85")
        self.canvas2.create_line(480*3, self.yshift, 480*3, 1000, width=1.5, fill="gray85")
        self.canvas2.create_line(480*4, self.yshift, 480*4, 1000, width=1.5, fill="gray85")
        #self.print_children(self.canvas2)

    def option_changed(self):
        """
            When model choice is changed, resets the parameters.
        """
        # When model option is changed, initialization is changed 
        for i in range(len(self.label)):
            self.label[i].destroy()
            self.para_entry[i].destroy()
        self.label = []
        self.para_entry = []
        model_name = self.model_choice.get()
        self.modelvarq = self.model_attr[model_name]
        self.para_list = []
        for i in range(len(self.modelvarq)):
            tkvarq = StringVar(self.canvas2)
            self.para_list.append(tkvarq)
            self.para_wigets = self.create_wigets2(self.para_list[i], i)

    def create_wigets2(self, ga, order, print_para=FALSE):
        """
            Create entries for choosing parameters / printing parameters.
        """
        key, value = list(self.modelvarq.items())[order]
        if print_para:
            paddings = {'padx': 5, 'pady': 5}
            para_title = Label(self.canvas2, text='Parameters:',font='Helvetica 13 bold', fg='blue4')
            self.canvas2.create_window((self.mod_number*self.model_xpart)*160+20, self.yshift + 40, window=para_title, anchor=W)
            self.label_entry[self.mod_number].append(Label(self.canvas2, text=f'{key} = {ga.get()}'))
            self.canvas2.create_window((self.mod_number*self.model_xpart)*160+190, self.yshift + 40 + order * 20, window=self.label_entry[self.mod_number][order], anchor=W)
            #self.label_entry[self.mod_number][order].grid(column = model_order*self.model_xpart+2, row=order+9, sticky=W, **paddings, columnspan=self.model_xpart)
        else:
            self.label.append(Label(self.canvas2, text=f'Please Select {key}:',takefocus=0,font='Helvetica 12 bold'))
            self.canvas2.create_window((380+order*280, 20), window=self.label[order], anchor=W)

            # Parameter Entries
            self.para_entry.append(Entry(
                self.canvas2,
                textvariable=ga,
                font=('calibre', 10, 'normal')))
            self.para_entry[order].insert(0,value)
            self.canvas2.create_window((500+order*280, 20), window=self.para_entry[order], anchor=W)

    def consensus_ranking(self):
        """
            Compute consensus ranking for the current model.
        """
        # Create consensus ranking area
        model_name = self.model_choice.get()

        if model_name not in self.model_order:
            self.move = True
            self.model_order.append(model_name)
            self.mod_number = len(self.model_order) - 1
            label = Label(self.canvas2, text=(model_name + " Model"), font=('Comic Sans MS', 15),takefocus=0)
            self.canvas2.create_window((self.mod_number * self.model_xpart) * 160 + 150, self.yshift + 15, window=label, anchor=W)
        else:
            self.mod_number = self.model_order.index(self.model_choice.get())
            for i in range(len(self.label_entry[self.mod_number])):
                self.label_entry[self.mod_number][i].destroy()
            self.label_entry[self.mod_number] = []
            self.move = False
            if model_name == "RIM":
                if self.image is not None:
                    self.image[0].close()

        self.para_dict = {}
        for i in range(len(self.para_list)):
            self.para_wigets = self.create_wigets2(self.para_list[i], i, print_para=TRUE)
            self.para_dict[list(self.model_attr[model_name].keys())[i]] = self.para_list[i].get()

        self.para_dict_list[model_name] = self.para_dict

        if model_name == "Landmarks":
            self.input_path = self.ratings_path
        else:
            self.input_path = self.rankings_path


        self.instance = java_import(self.input_path, model_name, self.para_dict, self.rankings_names["short"],
                                    self.directory.get())

        if model_name != "Borda":
            print(self.instance.argument)
            self.instance.execute_java()
        self.combine_results()
        if model_name == "Landmarks" or model_name == "GMM" or model_name == "Mallows":
            self.display_rankings(model_name)
        if model_name == "RIM":
            self.display_rim()
        if model_name == "Borda":
            self.display_borda()
            mod_name, path, type = self.borda_type()

        if model_name != "Borda":
            self.gui.results[model_name] = self.results[model_name]
        else:
            for imod in range(len(mod_name)):
                mod = mod_name[imod]
                self.gui.results[mod] = self.results[mod]
        self.gui.cen_rankings = self.get_cen_rankings()
        self.gui.display_rankings()


    def borda_type(self):
        """
            Assigns types for Borda depending on the dataset.

            Returns:
                model_name (list): list of Borda names.
                path (list): list of data paths.
                type (list): list of data types.
        """
        if self.type == "Both":
            model_name = ["Borda (Ratings)", "Borda (Rankings)"]
            path = [self.ratings_path, self.rankings_path]
            type = ["Rate", "Rank"]
        elif self.type == "Rank":
            model_name = ["Borda (Rankings)"]
            path = [self.rankings_path]
            type = ["Rank"]
        elif self.type == "Rate":
            model_name = ["Borda (Ratings)"]
            path = [self.ratings_path]
            type = ["Rank"]

        return model_name, path, type

    def display_borda(self, ranking=None):
        """
             Display rankings, thetas and costs for the Borda model.
        """
        xadjust = -20

        if ranking is None:
            model_name, path, type = self.borda_type()

        for imod in range(len(model_name)):
            mod = model_name[imod]
            input_path = path[imod]
            if ranking is None:
                ranking = self.instance.borda(input_path,type=type[imod])[0]
            thetas = self.results[mod]['theta']

            self.get_ranking_pos(ranking)
            self.label_entry[self.mod_number].append(
                Label(self.canvas2, text= mod + '\n Ranking:', font='Helvetica 13 bold', fg='blue4'))
            self.canvas2.create_window((self.mod_number * self.model_xpart) * 160 + 100 + xadjust + imod * self.model_xpart * 70, self.yshift + 50,
                                    window=self.label_entry[self.mod_number][-1])

            font = ("Times New Roman bold", 12)

            for iranking in range(len(ranking)):
                rk = ranking[iranking]
                pos = self.Consensus_pos[iranking]
                self.rect = self.canvas2.create_rectangle(pos[0] + xadjust + imod * self.model_xpart * 70, pos[2], pos[1]+ xadjust + imod * self.model_xpart * 70, pos[3], fill="gray90", outline="gray90",
                                                      width=3)
                self.text = self.canvas2.create_text((pos[0] + pos[1]) // 2 + imod * self.model_xpart * 70 + xadjust,
                                                     (pos[2] + pos[3]) // 2,
                                                    font=font, text=self.rankings_names["short"][rk],
                                                    fill="black")
                self.label_entry[self.mod_number].append([self.rect, self.text])

            self.label_entry[self.mod_number].append(
                Label(self.canvas2, text="Q Col Sums", font='Helvetica 13 bold', fg='blue4'))
            self.canvas2.create_window((self.mod_number * self.model_xpart) * 160 + 200 + xadjust + imod * self.model_xpart * 70, self.yshift + 50,
                                   window=self.label_entry[self.mod_number][-1])

            for itheta in range(len(thetas)):
                pos = self.Consensus_pos[itheta]
                self.rect = self.canvas2.create_rectangle(pos[0] + 100 + imod * self.model_xpart * 70 + xadjust, pos[2],
                                                          pos[1] + 100 + imod * self.model_xpart * 70 + xadjust, pos[3], fill="gray90", outline="gray90",
                                                        width=3)
                self.text = self.canvas2.create_text((pos[0] + pos[1]) // 2 + 100 + imod * self.model_xpart * 70 + xadjust, (pos[2] + pos[3]) // 2,
                                                    font=font, text=f'{round(thetas[itheta], 2)}', fill="black")

                self.label_entry[self.mod_number].append([self.rect, self.text])

    def display_rankings(self, model_name, ranking=None):
        """
            Display rankings, thetas and costs for Mallows, GMM.
        """
        # Display rankings, thetas and costs for current model
        def rgbcolor(theta):
            prob = np.exp(-(theta)) / (1 + np.exp(-(theta)))
            rgb = (int(prob* 255), 0, int((1-prob)* 255))
            return "#%02x%02x%02x" % rgb
        if ranking is None:
            ranking = self.instance.cen_rankings

        cost = self.results[model_name]['cost']
        thetas = self.results[model_name]['theta']


        if model_name == "GMM" or model_name == "Mallows":
            self.label_entry[self.mod_number].append(
                Label(self.canvas2, text='Default: AStar', font='Helvetica 13 bold', fg='blue4'))
            self.canvas2.create_window((self.mod_number * self.model_xpart) * 160 + 250, self.yshift + 50,
                                       window=self.label_entry[self.mod_number][-1], anchor=W)

        self.label_entry[self.mod_number].append(Label(self.canvas2, text='Cost:', font='Helvetica 13 bold', fg='blue4'))
        self.canvas2.create_window((self.mod_number * self.model_xpart) * 160 + 150, self.yshift + 50,
                                   window=self.label_entry[self.mod_number][-1], anchor=W)
        self.label_entry[self.mod_number].append(Label(self.canvas2, text= f'{round(cost,2)}', font='Helvetica 13'))
        self.canvas2.create_window((self.mod_number * self.model_xpart) * 160 + 190, self.yshift + 50,
                                   window=self.label_entry[self.mod_number][-1], anchor=W)

        self.get_ranking_pos(ranking)
        self.label_entry[self.mod_number].append(Label(self.canvas2, text='Ranking:', font='Helvetica 13 bold', fg='blue4'))
        self.canvas2.create_window((self.mod_number * self.model_xpart) * 160 + 120, self.yshift + 80,
                                   window=self.label_entry[self.mod_number][-1])

        font = ("Times New Roman bold", 12)


        if  model_name != "Landmarks":
            for iranking in range(len(ranking)):
                rk = ranking[iranking]
                pos = self.Consensus_pos[iranking]
                rect = self.canvas2.create_rectangle(pos[0], pos[2], pos[1], pos[3], fill="gray90", outline="gray90", width=3)
                text = self.canvas2.create_text((pos[0] + pos[1]) // 2, (pos[2] + pos[3]) // 2,
                                                        font=font,text=self.rankings_names["short"][rk],
                                                        fill="black")
                self.label_entry[self.mod_number].extend([rect,text])

        else:
            total = self.instance.landmarks
            self.get_ranking_pos(total)
            landmarks = [1,2,3,4]
            nlandmarks = len(total) - len(self.rankings_names['long'])
            color = ['gray90','gray80','gray70','gray60','gray50','gray40'][:(nlandmarks+1)]
            iland = 0
            for i in range(len(total)):
                if total[i] >= len(self.rankings_names['long']):
                    iland = iland + 1
                    pos = self.Consensus_pos[i-iland+1]
                    line = self.canvas2.create_line(pos[0]-15,pos[2]-2,pos[1]+15, pos[2]-2, fill=color[iland], width=2)
                    text2 = self.canvas2.create_text(pos[0]-10, pos[2]+10,font='Helvetica 12 bold',text=f'{landmarks[::-1][iland-1]}',
                                                            fill=color[iland])
                    self.label_entry[self.mod_number].extend([line, text2])

                else:
                    rk = total[i]
                    pos = self.Consensus_pos[i-iland]
                    rect = self.canvas2.create_rectangle(pos[0], pos[2], pos[1], pos[3], fill=color[iland], outline=color[iland], width=3)
                    text = self.canvas2.create_text((pos[0] + pos[1]) // 2, (pos[2] + pos[3]) // 2,
                                                            font=font,text=self.rankings_names["short"][rk],
                                                            fill="black")
                    self.label_entry[self.mod_number].extend([rect,text])


        #self.label_entry[self.mod_number].append(Label(self.canvas2, text=u'\u03b8:', font='Helvetica 13 bold', fg='blue4'))
        #self.canvas2.create_window((self.mod_number * self.model_xpart) * 160 + 250, self.yshift + 80, window=self.label_entry[self.mod_number][-1])

        self.label_entry[self.mod_number].append(
            Label(self.canvas2, text=u'exp(-\u03b8):', font='Helvetica 13 bold', fg='blue4'))
        self.canvas2.create_window((self.mod_number * self.model_xpart) * 160 + 320, self.yshift + 80,
                                   window=self.label_entry[self.mod_number][-1])

        for itheta in range(len(thetas)):
            pos = self.Consensus_pos[itheta]
            color = rgbcolor(thetas[itheta])
            #self.rect1 = self.canvas2.create_rectangle(pos[0] + 150, pos[2], pos[1] + 150, pos[3], fill=color, outline=color, width=3)
            #self.text1 = self.canvas2.create_text((pos[0] + pos[1]) // 2 + 150, (pos[2] + pos[3]) // 2,
                                                     #font=font,text=f'{round(thetas[itheta], 2)}',fill="white")

            self.rect2 = self.canvas2.create_rectangle(pos[0] + 200, pos[2], pos[1] + 200, pos[3], fill=color,
                                                       outline=color, width=3)
            self.text2 = self.canvas2.create_text((pos[0] + pos[1]) // 2 + 200, (pos[2] + pos[3]) // 2,
                                                 font=font, text=f'{round(np.exp(-thetas[itheta]), 2)}', fill="white")

            self.label_entry[self.mod_number].extend([self.rect2,self.text2])


    def display_rim(self):
        """
            Display results for RIM model (with image).
        """
        model_name = "RIM"
        cost = self.results[model_name]['cost']

        self.label_entry[self.mod_number].append(Label(self.canvas2, text='Cost:', font='Helvetica 13 bold', fg='blue4'))

        self.canvas2.create_window((self.mod_number * self.model_xpart) * 160 + 150, self.yshift + 100,
                                   window=self.label_entry[self.mod_number][-1], anchor=W)

        self.label_entry[self.mod_number].append(
            Label(self.canvas2, text= f'{round(cost, 2)}', font='Helvetica 13'))
        self.canvas2.create_window((self.mod_number * self.model_xpart) * 160 + 190, self.yshift + 100,
                                   window=self.label_entry[self.mod_number][-1], anchor=W)

        address = self.results[model_name]['image']
        if self.move:
            self.image.append(PIL.Image.open(address))
            self.treeplot.append(PIL.ImageTk.PhotoImage(self.image[0]))
        else:
            self.image[0] = PIL.Image.open(address)
            self.treeplot[0] = PIL.ImageTk.PhotoImage(self.image[0])

        self.canvas2.create_image(((self.mod_number*self.model_xpart) * 160 + 230, 23 * 10 + self.yshift + 100), image = self.treeplot[0])


    def combine_results(self):
        """
           Save model results in self.results.

           self.results is a dict of dict.
        """
        model_name = self.model_choice.get()
        if model_name == "Mallows" or model_name == "GMM":
            results = self.instance.results
            the = results[-1].split()
            thetas = []
            for j in the[2:]:
                thetas.append(float(j))
            cost = self.instance.results[0]
            ranking = self.instance.cen_rankings
        elif model_name == "Landmarks":
            cost = -self.instance.results[2][0]
            thetas = []
            mylist = list(self.instance.results[1])
            for i in range(len(self.rankings_names['long'])):
                thetas.append(float(mylist[i]))
            ranking = self.instance.cen_rankings
        elif model_name == "RIM":
            cost = float(self.instance.results[2])
            thetas = []
            ranking = self.instance.cen_rankings
        elif model_name == "Borda":
            mod_name, path, type = self.borda_type()

            for imod in range(len(mod_name)):
                mod = mod_name[imod]
                input_path = path[imod]
                compute = self.instance.borda(input_path, type=type[imod])
                ranking = compute[0]
                thetas = compute[1]
                cost = None
                self.results[mod] = {'ranking': ranking,
                                      'theta': thetas,
                                       'cost': cost}

        if model_name != "Borda":
            self.results[model_name] = {'ranking': ranking,
                                        'theta': thetas,
                                        'cost': cost}

        if model_name == 'RIM':
            self.results[model_name]['image'] = self.directory.get() + "/" + model_name + "/" + model_name + ".png"

        if model_name == "Landmarks":
            self.results[model_name]['total'] = self.instance.landmarks
    def get_cen_rankings(self):
        """
            Get consensus ranking from the current model.

            Returns:
                cen_rankings (list): list of consensus rankings
        """
        cen_rankings = []
        for item in self.instance.cen_rankings:
            if item < len(self.rankings_names["long"]):
                cen_rankings.append(self.rankings_names["short"][item])
        return cen_rankings

    def get_ranking_pos(self, rankings):
        """
            Compute coordinates of consensus rankings in each model area.
        """
        self.Consensus_pos = []
        for i in range(len(rankings)):
            self.Consensus_pos.append(((self.mod_number * self.model_xpart) * 160 - self.box_width // 2 + 120,
                                       (self.mod_number * self.model_xpart) * 160 + self.box_width // 2 + 120,
                                        self.yshift + 110 + i * 30 - self.box_height // 2,
                                        self.yshift + 110 + i * 30 + self.box_height // 2))



    # Help functions for buttons
    def set_working_directory(self):
        """
            Widget for selecting working directory and printing it next to the button..
        """
        self.directory.set(filedialog.askdirectory(initialdir=self.directory.get()+"/Output"))
        directorypathText = Label(self.canvas2, textvariable=self.directory)
        #directorypathText.grid(row=2, column=4, sticky=W, columnspan=5)
        self.canvas2.create_window((200, self.button_yshift + 20), window=directorypathText, anchor=W)
        self.write_data_txt()

    def reloadmodel(self):
        """
            Selecting model results file (.json) for loading and display the results on canvas.
        """
        filename = filedialog.askopenfilename(title="Select a File",
                                            filetypes=[('Json File', '*.json')],
                                            initialdir=self.directory.get())
        self.models_path.set(filename)
        filepathText = Label(self.canvas2, textvariable=self.models_path)
        #filepathText.grid(row=4, column=4, sticky=W, columnspan=5)
        self.canvas2.create_window((250, 3*self.button_yshift + 20), window=filepathText, anchor=W)

        f = open(filename, 'r')
        try:
            data = json.load(f)
            self.para_dict_list = data["parameters"]
            self.results = data["results"]
            model_names = data["parameters"].keys()
            i = 0
            for model_name in model_names:
                self.mod_number = i
                if (model_name == "Landmarks" or model_name == "GMM" or
                        model_name == "Mallows"):
                    self.display_rankings(model_name, ranking=self.results[model_name]['ranking'])
                if model_name == "RIM":
                    self.display_rim()
                if model_name == "Borda (Rankings)" or "Borda (Ratings)":
                    self.display_borda(ranking=self.results[model_name]['ranking'])
                i += 1

        except:
            print("Error loading json file")


    def save_model(self):
        """
            Save current model results to a .json file.
        """
        file_dir = os.path.join(self.directory.get(), "/model.json")
        try:
            data = {
                "parameters": self.para_dict_list,
                "results": self.results
            }
            with open(file_dir, "w") as f:
                json.dump(data, f)
                f.close()
            self.saveText = Label(self.canvas2, text="Model Saved!")
            self.canvas2.create_window((200, 6 * self.button_yshift + 20), window=self.saveText, anchor=W)

        except Exception as e:
            print("error saving state:", str(e))



    #Printing labels on the buttons for writing the manual
    def print_children(self, parent):
        """
            Print texts on buttons to a buttons_names.txt.
            Not using.
        """
        finList = []
        children = parent.winfo_children()
        for item in children:
            try:
                finList.append(item.cget('text'))
            except:
                print(item)
        with open(self.directory.get() +'/buttons_names.txt', 'w') as f:
            for line in finList:
                f.write(f"{line}\n")


    def generate_bootstrap(self, nBoot, model):
        """
            Generate bootstrap samples and compute the results.
        """
        if model == "Landmarks" or model == "Borda (Ratings)":
            self.ratings_np = self.ratings.to_numpy()
            files = {"Rate": self.ratings_np}
        else:
            self.rankings_np = self.rankings.to_numpy()
            files = {"Rank": self.rankings_np}
        if model == "Borda (Ratings)" or model == "Borda (Rankings)":
            model = "Borda"

        for label, filemat in files.items():
            bootstrap_path = self.directory.get() + "/bootstrap/" + label + ".txt"
            n = filemat.shape[0]
            sample = np.random.choice(range(n), size=n * nBoot)
            mat = np.zeros((n * nBoot, filemat.shape[1]))
            for i in range(n * nBoot):
                mat[i] = filemat[sample[i]]

            isExist = os.path.exists(self.directory.get() + "/bootstrap")
            bootstrap = StringVar(self.canvas2)
            bootstrap.set(bootstrap_path)

            if not isExist:
                os.makedirs(self.directory.get() + "/bootstrap")
            else:
                if os.path.isfile(bootstrap_path):
                    os.remove(bootstrap_path)

            with open(bootstrap_path, "w") as f:
                for line in mat:
                    f.write(' '.join([str(int(a)) for a in line]) + '\n')

            self.instance = java_import(bootstrap_path, model, self.para_dict,
                                        self.rankings_names["short"], self.directory.get() + "/bootstrap", nBoot)
            if model != "Borda":
                self.instance.execute_java()
            else:
                self.instance.borda(bootstrap_path, type=label)

        return self.directory.get()







