import pandas as pd
import numpy as np


class rankings:
    def __init__(self, file_path, other_paths):
        self.df = pd.read_csv(file_path, header=0, index_col=0)
        self.rating_names = list(other_paths.keys())
        self.ratings = {}
        for rate_name in other_paths.keys():
            self.ratings[rate_name] = pd.read_csv(other_paths[rate_name], header=0, index_col=0)
        self.op = self.ratings[self.rating_names[0]]

    def get_all_sub_ratings(self):
        return self.rating_names
    
    def get_sub_rating(self, rat_name, reviewer, prop):
        return self.ratings[rat_name].loc[reviewer, prop]

    def get_columns(self):
        return list(self.df.index)

    def get_num_rows(self):
        return len(self.df.columns)

    def get_all_rankings(self):
        rows = list(self.df.index)
        ret_list = []
        for i in range(len(rows)):
            ordered_list = list(self.df.iloc[i].sort_values(ascending=True).index)
            ret_list.append(ordered_list)
        return ret_list

    def get_op_rankings(self):
        ret = {}
        rows = list(self.op.index)
        props = list(self.op.columns)
        maxi = 0
        for reviewer in rows:
            ret[reviewer] = {}
            for prop in props:
                rate = self.op.loc[reviewer, prop]
                if not np.isnan(rate):
                    if rate not in ret[reviewer]:
                        ret[reviewer][rate] = [prop]
                    else:
                        ret[reviewer][rate].append(prop)
                        if len(ret[reviewer][rate]) > maxi:
                            maxi = len(ret[reviewer][rate])
        return ret, maxi