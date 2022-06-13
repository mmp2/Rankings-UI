import pandas as pd
import numpy as np

from pre_process import distr_df


class Rankings:
    def __init__(self, ranking_path, rating_df):
        self.scores = rating_df
        self.ranking_path = ranking_path
        self.ranking, self.ties = self.rankings(ranking_path)
        self.rating_names = self.scores.columns[4:-1]

        self.index = list(self.scores["Reviewer Name"].unique())
        self.columns = list(self.scores["Paper Short Name"].unique())
        self.num_papers = len(self.columns)

    def get_rating_df(self, rat_name):
        df = pd.DataFrame(index=self.scores["Reviewer Name"].unique(), columns=self.scores["Paper Short Name"].unique())
        for index in self.index:
            for column in self.columns:
                df.loc[index][column] = self.get_sub_rating(rat_name, index, column)
        return df

    def rankings(self, path):
        result = {}
        tied = {}
        with open(path, encoding="utf-8") as r:
            lines = r.read().splitlines()
            i = 1
            while i != len(lines):
                if lines[i] != "":
                    parts = lines[i].split("\t")
                    if self.get_name(parts[0]) not in result:
                        result[self.get_name(parts[0])] = []
                        tied[self.get_name(parts[0])] = []
                    left = self.get_prop_sname(int(parts[1]))
                    right = self.get_prop_sname(int(parts[3]))
                    if left in result[self.get_name(parts[0])] and right not in result[self.get_name(parts[0])]:
                        index = result[self.get_name(parts[0])].index(left)
                        if parts[2] == "Comparable":
                            result[self.get_name(parts[0])].insert(index, right)
                            exist = False
                            for i in range(len(tied[self.get_name(parts[0])])):
                                if left in tied[self.get_name(parts[0])][i]:
                                    tied[self.get_name(parts[0])][i].append(right)
                                    exist = True
                                    break
                                elif right in tied[self.get_name(parts[0])][i]:
                                    tied[self.get_name(parts[0])][i].append(left)
                                    exist = True
                                    break
                            if not exist:
                                tied[self.get_name(parts[0])].append([left, right])
                            #elif right in set(x for x in tied[self.get_name(parts[0])]):
                                #tied[self.get_name(parts[0])].append(left)
                            #else:
                                #tied[self.get_name(parts[0])].extend([left, right])
                        else:
                            result[self.get_name(parts[0])].insert(index+1, right)
                    elif right in result[self.get_name(parts[0])] and left not in result[self.get_name(parts[0])]:
                        index = result[self.get_name(parts[0])].index(right)
                        if parts[2] == "Comparable":
                            result[self.get_name(parts[0])].insert(index, left)
                            exist = False
                            for i in range(len(tied[self.get_name(parts[0])])):
                                if left in tied[self.get_name(parts[0])][i]:
                                    tied[self.get_name(parts[0])][i].append(right)
                                    exist = True
                                    break
                                elif right in tied[self.get_name(parts[0])][i]:
                                    tied[self.get_name(parts[0])][i].append(left)
                                    exist = True
                                    break
                            if not exist:
                                tied[self.get_name(parts[0])].append([left, right])
                        else:
                            result[self.get_name(parts[0])].insert(index, left)
                    elif (len(result[self.get_name(parts[0])]) != 0) and (right not in result[self.get_name(parts[0])]) and (left not in result[self.get_name(parts[0])]):
                        lines.append(lines[i])
                    else:
                        result[self.get_name(parts[0])].append(left)
                        result[self.get_name(parts[0])].append(right)
                        if parts[2] == "Comparable":
                            exist = False
                            for i in range(len(tied[self.get_name(parts[0])])):
                                if left in tied[self.get_name(parts[0])][i]:
                                    tied[self.get_name(parts[0])][i].append(right)
                                    exist = True
                                    break
                                elif right in tied[self.get_name(parts[0])][i]:
                                    tied[self.get_name(parts[0])][i].append(left)
                                    exist = True
                                    break
                            if not exist:
                                tied[self.get_name(parts[0])].append([left, right])
                i += 1
        return result, tied

    def updated_pairs(self,  dict, topk):
        df = self.scores.copy()
        if dict is not None:
            for key in dict.keys():
                df = df[(dict[key][0] <= df[key]) & (df[key] <= dict[key][1])]
        df = df[["Reviewer Name", "Paper Short Name"]]
        dict_r = self.get_all_rankings(topk=topk)
        rank_list = [(i,x) for i in dict_r for x in dict_r[i]]
        filter_list = list(df.itertuples(index=False, name=None))
        return list(set(rank_list).intersection(set(filter_list)))


    def get_name(self, email):
        return self.scores.loc[self.scores["Reviewer Email"] == email, "Reviewer Name"].iloc[0]

    def get_sub_rating(self, rat_name, reviewer, prop):

        l = self.scores.loc[(self.scores["Reviewer Name"] == reviewer) & (self.scores["Paper Short Name"] == prop), rat_name].tolist()
        if l:
            return l[0]
        else:
            return np.nan

    def get_all_sub_ratings(self):
        return list(self.rating_names)

    def get_columns(self):
        return list(self.index)

    def get_all_rankings(self, topk=None):
        ret = {}
        for key in self.index:
            papers = self.ranking[key]
            selected = papers
            if topk is not None:
                selected = papers[:topk]
                for tie in self.ties[key]:
                    for i in range(len(tie)):
                        if selected[-1] == tie[i]:
                            for other in tie:
                                if other not in selected:
                                    selected.append(other)
                            break
            ret[key] = selected
        return ret

    def get_prop_sname(self, id):
        return self.scores.loc[self.scores["Paper ID"] == id, "Paper Short Name"].iloc[0]

    def visible_rects(self):
        pass

    def get_op_rankings(self):
        list_rank = self.get_all_rankings()
        df_op = self.get_rating_df("Overall Score")
        #for i in range(len(list_rank)):
            #for paper in list(df_op.columns):
                #if paper not in list_rank[i]:
                    #df_op.at[list(df_op.index)[i], paper] = np.nan
        ret = {}
        rows = list(self.index)
        props = list(self.columns)
        maxi = 0
        for reviewer in rows:
            ret[reviewer] = {}
            for prop in props:
                rate = df_op.loc[reviewer, prop]
                if not np.isnan(rate):
                    if rate not in ret[reviewer]:
                        ret[reviewer][rate] = [prop]
                    else:
                        ret[reviewer][rate].append(prop)
                        if len(ret[reviewer][rate]) > maxi:
                            maxi = len(ret[reviewer][rate])
        return ret, maxi

'''
RATINGS_PATH = "dummy_ICML.xls"
RANKING = "ReviewerSubmissionComparisons.txt"
scores_path = RATINGS_PATH
ranking_path = RANKING 
ratings, props, reviewers, reivews = distr_df(scores_path)
ins = Rankings(ranking_path, ratings)
dict = {'Overall Score': [4, 5], 
    'Relevance and Significance': [4, 5], 
    'Novelty': [0, 4], 
    'Technical Quality': [0, 5], 
    'Experimental Evaluation': [0, 5]}

ins.updated_pairs(dict)
'''