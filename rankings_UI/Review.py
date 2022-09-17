import pandas as pd
pd.options.display.max_colwidth = 1000
import textwrap
class Reviews:
    def __init__(self, df, review_titles, prop_colname="Proposal Name", reviewer_colname="Reviewer Name", str_wrap_len=35) -> None:
        self.df = df
        self.prop_colname = prop_colname
        self.reviewer_colname = reviewer_colname
        self.review_titles = review_titles
        self.str_wrap_len = str_wrap_len

    def get_all_review_sub(self, reviewer, proposal):
        ret = []
        for title in self.review_titles:
            sent = self.df[(self.df[self.prop_colname] == proposal) & (self.df[self.reviewer_colname] == reviewer)][title]
            if len(sent) != 0:
                ret.append(sent.to_string(index=False))
            else:
                ret.append("NaN")
        return ret

    def wrap(self, string):
        return '\n'.join(textwrap.wrap(string, self.str_wrap_len))
    
    def get_reviews_in_order(self, reviewer, proposal, order):
        ret = []
        for i in range(len(order)):
            if order[i] in self.df.columns:
                sent = self.df[(self.df[self.prop_colname] == proposal) & (self.df[self.reviewer_colname] == reviewer)][order[i]]
                if len(sent) != 0:
                    ret.append(self.wrap(sent.to_string(index=False)))
                else:
                    ret.append("NaN")
        return ret