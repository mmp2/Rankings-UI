import pandas as pd
import numpy as np

class Rankings:
    def __init__(self, rating_df, ranking, ties, rating_names, reviewer_col_name="Reviewer Name", prop_col_name="Proposal Name", overall_col_name="Overall Score"):
        self.scores = rating_df
        self.ranking = ranking
        self.ties = ties
        self.rating_names = rating_names
        self.reviewer_col_name = reviewer_col_name
        self.overall_col_name = overall_col_name
        self.proposal_col_name = prop_col_name
        self.index = list(self.scores[self.reviewer_col_name].unique())
        self.columns = list(self.scores[self.proposal_col_name].unique())
        self.num_papers = len(self.columns)

    def get_rating_df(self, rat_name):
        df = pd.DataFrame(index=self.scores[self.reviewer_col_name].unique(), columns=self.scores[self.proposal_col_name].unique())
        for index in self.index:
            for column in self.columns:
                df.loc[index][column] = self.get_sub_rating(rat_name, index, column)
        return df

    def updated_pairs(self, dict, yesno, topk):
        df = self.scores.copy()
        if dict is not None:
            for key in dict.keys():
                df = df[(dict[key][0] <= df[key]) & (df[key] <= dict[key][1])]
        if yesno is not None:
            for key in yesno.keys():
                df = df[(df[key] == yesno[key])]
        df = df[[self.reviewer_col_name, self.proposal_col_name]]
        dict_r = self.get_all_rankings(topk=topk)
        rank_list = [(i,x) for i in dict_r for x in dict_r[i]]
        filter_list = list(df.itertuples(index=False, name=None))
        return list(set(rank_list).intersection(set(filter_list)))

    def get_name(self, email):
        return self.scores.loc[self.scores["Reviewer Email"] == email, self.reviewer_col_name].iloc[0]

    def get_sub_rating(self, rat_name, reviewer, prop):
        l = self.scores.loc[(self.scores[self.reviewer_col_name] == reviewer) & (self.scores[self.proposal_col_name] == prop), rat_name].tolist()
        if l:
            return str(l[0])
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
                if self.ties is not None:
                    for tie in self.ties[key]:
                        for i in range(len(tie)):
                            if selected[-1] == tie[i]:
                                for other in tie:
                                    if other not in selected:
                                        selected.append(other)
                                break
            ret[key] = selected
        return ret

    def get_op_rankings(self):
        df_op = self.get_rating_df(self.overall_col_name)
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