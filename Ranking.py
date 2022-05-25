import pandas as pd
import numpy as np


class Rankings:
    def __init__(self, ranking_path, rating_df):


        self.scores = rating_df
        self.ranking = self.rankings(ranking_path)
        self.rating_names = self.scores.columns[4:-1]

        self.index = list(self.scores["Reviewer Name"].unique())
        self.columns = list(self.scores["Paper Short Name"].unique())

    def get_rating_df(self, rat_name):
        df = pd.DataFrame(index=self.scores["Reviewer Name"].unique(), columns=self.scores["Paper Short Name"].unique())
        for index in self.index:
            for column in self.columns:
                df.loc[index][column] = self.get_sub_rating(rat_name, index, column)
        return df

    def rankings(self, path):
        result = {}
        with open(path, encoding="utf-8") as r:
            lines = r.read().splitlines()
            i = 1
            while i != len(lines):
                if lines[i] != "":
                    parts = lines[i].split("\t")
                    if parts[0] not in result:
                        result[parts[0]] = []
                    left = parts[1]
                    right = parts[3]
                    if left in result[parts[0]] and right not in result[parts[0]]:
                        index = result[parts[0]].index(left)
                        if parts[2] == "Comparable":
                            result[parts[0]].insert(index, right)
                        else:
                            result[parts[0]].insert(index+1, right)
                    elif right in result[parts[0]] and left not in result[parts[0]]:
                        index = result[parts[0]].index(right)
                        if parts[2] == "Comparable":
                            result[parts[0]].insert(index, left)
                        else:
                            result[parts[0]].insert(index, left)
                    elif (len(result[parts[0]]) != 0) and (right not in result[parts[0]]) and (left not in result[parts[0]]):
                        lines.append(lines[i])
                    else:
                        result[parts[0]].append(left)
                        result[parts[0]].append(right)
                i += 1
        return result
    
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

    def get_all_rankings(self):
        ret = []
        for key in self.ranking.keys():
            l = []
            for id in self.ranking[key]:
                l.append(self.get_prop_sname(int(id)))
            ret.append(l)  
        return tuple(ret)

    def get_prop_sname(self, id):
        return self.scores.loc[self.scores["Paper ID"] == id, "Paper Short Name"].iloc[0]

    def get_op_rankings(self):
        df_op = self.get_rating_df("Overall Score")
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


''''
RATINGS_PATH = "dummy_ICML.xls"
RANKING = "ReviewerSubmissionComparisons.txt"

instance = rankings(RANKING, RATINGS_PATH)
#print(instance.get_op_rankings())
print(instance.rankings)
'''