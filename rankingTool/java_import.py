import os.path,subprocess

from subprocess import STDOUT,PIPE
import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages
import rpy2.robjects.numpy2ri as rpyn
from rpy2.robjects.vectors import StrVector
import numpy as np


class java_import:
    """
        Class for sending dataset to packages and organizing results.

        Attributes:
        -----
            input_path (str): Path to the input dataset.
            model_choice (str): Name of the model.
            params (dict): Parameters for the model.
            rankings_names (list): Names of the proposals.
            directory (str): Directory for saving the interim files and outputs.
            nBoot (int): Number of bootstrap samples. nBoot=1 suggests no bootstrap is used.

        Methods:
        -----
            execute_java():
                Run java packages for models RIM, Landmarks, GMM and Mallows.
            gmm_output():
                Reading and organizing output from the GMM package.
            routput():
                Reading and organizing output from the RIM package.
            rlandmarks(out=False):
                If out=True, organize output from the Landmarks package; otherwise, organize the input.
            write_gmm_txt(nBoot):
                Write the configuration file for GMM package.
            get_N():
                Get the number of rows in the input dataset.
            borda(path, type):
                Compute Borda rankings.
    """
    def __init__(self, input_path, model_choice, params, rankings_names, directory, nBoot=1) -> None:
        ## Params is a dictionary of parameter names and values
        self.rankings_path = input_path
        self.method = "AStar"
        self.params = params
        self.model_choice = model_choice
        self.rankings_names = rankings_names
        self.directory = directory + "/" + model_choice
        self.nBoot = nBoot
        isExist = os.path.exists(self.directory)
        if not isExist:
            os.makedirs(self.directory)
        else:
            for file_name in os.listdir(self.directory):
                file = self.directory + file_name
                if os.path.isfile(file):
                    os.remove(file)

        self.get_N()
        if model_choice == "RIM":
            self.argument = "-permtest file=" + self.rankings_path
            self.java_file = "rankingTool/java/RIM/model/RIM_main.java"
            self.argument = self.argument + " ptest=0 pvalidation=0 dataSeed=400 runtimeSeed=400 nboot=" + str(nBoot)
            for i in range(len(self.params)):
                para, value = list(self.params.items())[i]
                self.argument = self.argument + " " + str(para) + "=" + str(value)
        elif model_choice == "Landmarks":
            with open(self.rankings_path) as f:
                firstline = f.readline()
                numbers = [int(float(x)) for x in firstline.split(" ")]
                self.java_file = "rankingTool/java/landmarks/testing.java"
            self.argument = "-ltest infile=" + self.directory + "/landmarks.txt" + " outfile=" + self.directory + "/landmarks_out.txt"
            self.argument = self.argument + " nboot=" + str(nBoot) + " n=" + str(len(numbers))
        elif model_choice == "GMM" or model_choice == "Mallows" or model_choice == "Greedy":
            self.write_gmm_txt(self.nBoot)
            self.java_file = "gmm.ExptsManager"



    def execute_java(self):
        """
            Execute the java package and use the correct function for organizing outputs.
        """
        if self.model_choice == "Landmarks":
            self.rlandmarks()
            cmd = ['java', self.java_file] + self.argument.split()
        elif self.model_choice == "RIM":
            cmd = ['java', self.java_file] + self.argument.split()
        else:
            cmd = ['java', '-Xms100M', '-Xmx1500M', '-classpath',
                   'rankingTool/java/',self.java_file] + self.argument.split()
        proc = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        stdout,stderr = proc.communicate()
        if self.nBoot == 1:
            if self.model_choice == "RIM":
                self.results = str(stdout).split("\\n")[:3]
                self.results[0] = self.results[0][2:]
                self.tree = self.results[1]
                self.routput()
            elif self.model_choice == "Landmarks":
                self.rlandmarks(out=True)
                n = len(self.rankings_names)
                self.cen_rankings = []
                self.landmarks = []
                mylist = list(self.results[0])
                for i in range(len(mylist)):
                    element = int(mylist[i])
                    self.landmarks.append(element)
                    if element < n:
                        self.cen_rankings.append(element)
            elif self.model_choice == "GMM" or self.model_choice == "Mallows":
                self.cen_rankings = []
                self.gmm_output()
        else:
            if self.model_choice == "GMM" or self.model_choice == "Mallows":
                self.gmm_output()
            if self.model_choice == "RIM":
                self.results = str(stdout).split("\\n")[:(3*self.nBoot-1)]
                self.tree=[]
                for i in range(self.nBoot):
                    self.tree.append(self.results[1+3*i])
                self.routput()
            if self.model_choice == "Landmarks":
                self.rlandmarks(out=True)



    def gmm_output(self):
        """
            This function organizes the output from the GMM package.
            If self.nBoot > 1, the output would be stored to the bootstrap package.
        """
        if self.nBoot == 1:
            self.results = []
            with open(self.directory + "/gmm_dump.txt", "r") as f:
                searchlines = f.readlines()
            beamsearch = False
            for i, line in enumerate(searchlines):
                if 'Reverted to beam search.' in line:
                    beamsearch = True
                if 'Iteration 3' in line:
                    if self.model_choice == "GMM" or self.model_choice == "Mallows":
                        if self.method == "AStar":
                            if beamsearch:
                                region = searchlines[(i+7):(i+10)]
                            else:
                                region = searchlines[(i+6):(i+9)]
                        else:
                            if beamsearch:
                                region = searchlines[(i+6):(i+9)]
                            else:
                                region = searchlines[(i+5):(i+8)]
            for l in region:
                self.results.append(l)
            if self.method == "AStar":
                self.results[0] = self.results[0].split()
                self.results[0] = float(self.results[0][1])
            else:
                self.results[0] = self.results[0].split()
                self.results[0] = float(self.results[0][1])
            r = region[-2].split()
            for i in r[2:]:
                self.cen_rankings.append(int(i)-1)
        else:
            with open(self.directory + "/gmm_dump.txt", "r") as f:
                searchlines = f.readlines()
            for i, line in enumerate(searchlines):
                if 'Iteration 3' in line:
                    if self.model_choice == "GMM" or self.model_choice == "Mallows":
                        #temp = np.arange(3,4+2*(self.nBoot-1),step=2,dtype=int)
                        #print(temp)
                        if self.method == "AStar":
                            region = searchlines[(i+3):(i+4+2*(self.nBoot-1))]
                        else:
                            region = searchlines[(i+4):(i+5+2*(self.nBoot-1))]
            self.mat = np.zeros((self.nBoot,len(self.rankings_names)))
            ir = 0
            temp = np.arange(0, 1 + 2 * (self.nBoot - 1), step=2, dtype=int)
            for itemp in temp:
                l = region[itemp]
                temp = l.split()
                j = 0
                for i in temp[2:]:
                    self.mat[ir][j] = int(i) - 1
                    j += 1
                ir += 1
            with open(self.directory + "/bootcentral.txt", "w") as f:
                for line in self.mat:
                    f.write(','.join([str(int(a)) for a in line]) + '\n')




    def routput(self):
        """
            This function sorts the output from the RIM package and plot the tree.
        """
        packnames = ('stringr', 'plotrix', 'latex2exp', 'grDevices', 'base','imguR')
        utils = rpackages.importr('utils')
        utils.chooseCRANmirror(ind=1)
        names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
        if len(names_to_install) > 0:
            utils.install_packages(StrVector(names_to_install))
        robjects.r.source("rankingTool/R/plotTree.r", encoding="utf-8")
        #doit = robjects.globalenv['doit']
        makeplot = robjects.globalenv['makeplot']
        if self.nBoot==1:
            mylist = list(makeplot(self.directory + "/" + self.model_choice + ".png", 1, self.tree, self.rankings_names))
            self.cen_rankings = []
            for i in range(len(mylist)):
                self.cen_rankings.append(int(mylist[i]))
        else:
            self.mat = np.zeros((self.nBoot, len(self.rankings_names)))
            for i in range(self.nBoot):
                tree = self.tree[i]

                mylist = makeplot(self.directory + "/" + self.model_choice + ".png", 0, tree, self.rankings_names)
                for j in range(len(mylist)):
                    self.mat[i][j] = mylist[j]

            with open(self.directory + "/bootcentral.txt", "w") as f:
                for line in self.mat:
                    f.write(','.join([str(int(a)) for a in line]) + '\n')




        #createpng = robjects.globalenv.find('png')
        #par =  robjects.globalenv.find('par')
        #closepng = robjects.globalenv.find('dev.off')
        #print(self.tree)
        #createpng("rankingTool/R/" + self.model_choice + ".png")
        #par(mfrow=(1,1), mar=(0.1,0.1,0.1,0.1))
        #       closepng()


    def rlandmarks(self, out=False):
        """
            This is a function for writing the input and output for the Landmarks algorithm.

            Parameters:
                out (bool, optional): If True, write arguments required for the test; otherwise organize the output.
        """
        packnames = ('stringr', 'plotrix', 'latex2exp', 'grDevices', 'base','imguR')
        utils = rpackages.importr('utils')
        utils.chooseCRANmirror(ind=1)
        names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
        if len(names_to_install) > 0:
            utils.install_packages(StrVector(names_to_install))
        robjects.r.source("rankingTool/R/landmarks.r", encoding="utf-8")
        landmarks = [1,2,3,4]
        #for i in range(len(self.params)):
            #para, value = list(self.params.items())[i]
        #landmarks.append(value)
        if out==False:
            inpath = self.rankings_path
            outpath = self.directory + '/landmarks.txt'
            maketest = robjects.globalenv['maketest']
            maketest(inpath, outpath, robjects.StrVector(self.rankings_names), robjects.FloatVector(landmarks))
        else:
            path = self.directory + '/landmarks_out.txt'
            readresults = robjects.globalenv['readresults']
            if self.nBoot==1:
                self.results = readresults(path, robjects.FloatVector(landmarks),0)
                self.cen_rankings = self.results[0]
            else:
                bootpath = self.directory + "/bootcentral.txt"
                readresults(path, robjects.FloatVector(landmarks), 1, bootpath)


    def write_gmm_txt(self, nBoot=1):
        '''
            Write the parameters into the file for GMM package to run.

            Parameters:
                nBoot (int): number of bootstrap samples.
        '''

        with open(self.rankings_path) as f:
            firstline = f.readline()
            numbers = [int(float(x)) for x in firstline.split(" ")]

        fpara = open(self.directory + "/gmm_parameters.txt", "w")
        paralist = []
        for i in range(len(self.params)):
            para, value = list(self.params.items())[i]
            paralist.append(str(para)+"="+str(value)+"\n")
        paralist.insert(0, "n=" + str(len(numbers)) + "\n")
        paralist.insert(1,"inputType="+ self.rankings_path +"\n")
        paralist.insert(2, "iterations=3\n")
        paralist.insert(3, "method="+self.method+"\n")
        paralist.insert(4, "nBoot="+str(nBoot)+"\n")
        paralist.insert(5, "theta=1\n")
        paralist.insert(6, "N="+str(int(self.N/nBoot))+"\n")

        if self.model_choice == "Mallows":
            paralist.insert(6, "GMM=false\n")
        else:
            paralist.insert(6, "GMM=true\n")

        fpara.writelines(paralist)
        fpara.close()

        self.argument = self.directory + "/gmm_parameters.txt" + " " + self.directory + "/gmm_results.txt" + " " + self.directory + "/gmm_dump.txt"

    def get_N(self):
        """
            Compute the number of items in the dataset.
        """
        self.N = 0
        with open(self.rankings_path) as f:
            lines = f.readlines()
            for line in lines:
                self.N += 1

    def borda(self,path,type):
        """
            Compute the Borda rankings.

            Parameters:
                path (str): the path of the dataset.
                type (str): if type = "Rate", the dataset contains ratings; if type = "Rank", the dataset contains  rankings.
        """
        ranking = np.loadtxt(path, delimiter=' ')
        n = len(self.rankings_names)
        Q = np.zeros((self.nBoot, n, n))
        for ib in range(self.nBoot):
            bsize = int(ranking.shape[0]/self.nBoot)
            for irow in range(bsize*ib, bsize*(ib+1)):
                for i in range(n):
                    for j in range(i + 1, n):
                        Q[ib][int(ranking[irow, i]) - 1][int(ranking[irow, j]) - 1] += 1.0 / ranking.shape[0]



        if self.nBoot == 1:
            if type == "Rank":
                colsum = np.sum(Q[0], axis=0)
                temp = colsum.argsort()
            elif type == "Rate":
                colsum = np.sum(ranking, axis=0)
                temp = (-colsum).argsort()
            self.cen_rankings = list(temp)
            return temp, colsum[temp]

        else:
            if type == "Rank":
                colsum = np.sum(Q, axis=1)
                temp = colsum.argsort(axis=1)
            elif type == "Rate":
                colsum = np.zeros((self.nBoot, n))
                for ib in range(self.nBoot):
                    bsize = int(ranking.shape[0] / self.nBoot)
                    temp0 = ranking[range(bsize * ib, bsize * (ib + 1)),]
                    colsum[ib,:] = np.sum(temp0, axis=0)
                temp = (-colsum).argsort(axis=1)

            with open(self.directory + "/" + type + "_bootcentral.txt", "w") as f:
                for line in temp:
                    f.write(','.join([str(int(a)) for a in line]) + '\n')




#rankings_path = "rankingTool/java/model/restaurants_clean.txt"
#model_choice = "gmm"
#params = dict(ptest=.3, pvalidation=.2, iters=1000, temp=.03, dataSeed=400, runtimeSeed=400)
#def main():
#    instance = java_import(rankings_path, model_choice, params)
#    (instance.argument)print
#    instance.execute_java()
#    instance.routput()

#if __name__ == "__main__":
#    main()