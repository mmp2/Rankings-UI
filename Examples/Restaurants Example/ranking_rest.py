import pandas as pd
import numpy as np

class Rankings:
    def __init__(self, rating_df, ranking, ties):
        self.scores = rating_df
        self.ranking = ranking
        self.ties = ties
        self.rating_names = self.scores.columns[4:-2]
        self.index = list(self.scores["Reviewer Name"].unique())
        self.columns = list(self.scores["Proposal Name"].unique())
        self.num_papers = len(self.columns)

    def get_rating_df(self, rat_name):
        df = pd.DataFrame(index=self.scores["Reviewer Name"].unique(), columns=self.scores["Proposal Name"].unique())
        for index in self.index:
            for column in self.columns:
                df.loc[index][column] = self.get_sub_rating(rat_name, index, column)
        return df

    def updated_pairs(self, dict, repo, topk):
        df = self.scores.copy()
        if dict is not None:
            for key in dict.keys():
                df = df[(dict[key][0] <= df[key]) & (df[key] <= dict[key][1])]
        df = df[df["Reproducibility"] == repo]
        df = df[["Reviewer Name", "Proposal Name"]]
        dict_r = self.get_all_rankings(topk=topk)
        rank_list = [(i,x) for i in dict_r for x in dict_r[i]]
        filter_list = list(df.itertuples(index=False, name=None))
        return list(set(rank_list).intersection(set(filter_list)))

    def get_sub_rating(self, rat_name, reviewer, prop):
        """
        Given a rating name, a reviewer name, and a proposal name, returns its score of rating.
        Return NaN if there is no such a score.
        """
        l = self.scores.loc[(self.scores["Reviewer Name"] == reviewer) & (self.scores["Proposal Name"] == prop), rat_name].tolist()
        if l:
            return str(l[0])
        else:
            return np.nan

    def get_all_sub_ratings(self):
        """
        Returns a list of sub-rating (not including op) names
        """
        return list(self.rating_names)

    def get_columns(self):
        """
        Returns a list of unique reviewer names.
        """
        return list(self.index)

    def get_op_rankings(self):
        """
        Return:
        ret: A dictionary of dictionaries that the first key is reviewer and the second key is the op rating score and 
            the value is a list of proposals.
        maxi: The maximum number of proposals that has a same op rating score.
        """
        df_op = self.get_rating_df("OP")
        ret = {}
        rows = list(self.index)
        props = list(self.columns)
        maxi = 0
        for reviewer in rows:
            ret[reviewer] = {}
            for prop in props:
                rate = df_op.loc[reviewer, prop]
                if not pd.isna(rate):
                    if rate not in ret[reviewer]:
                        ret[reviewer][rate] = [prop]
                    else:
                        ret[reviewer][rate].append(prop)
                        if len(ret[reviewer][rate]) > maxi:
                            maxi = len(ret[reviewer][rate])
        return ret, maxi
