import pandas as pd
pd.options.display.max_colwidth = 1000
import textwrap
class Reviews:
    def __init__(self, df) -> None:
        self.df = df

    def get_all_review_sub(self, reviewer, proposal):
        summary = self.df[(self.df["Paper Short Name"] == proposal) & (self.df["Reviewer Name"] == reviewer)]["Summary"].to_string(index=False)
        details = self.df[(self.df["Paper Short Name"] == proposal) & (self.df["Reviewer Name"] == reviewer)]["Detailed Comments"].to_string(index=False)
        quetsion = self.df[(self.df["Paper Short Name"] == proposal) & (self.df["Reviewer Name"] == reviewer)]["Questions for Author"].to_string(index=False)
        anonymity = self.df[(self.df["Paper Short Name"] == proposal) & (self.df["Reviewer Name"] == reviewer)]["Anonymity"].to_string(index=False)
        anonymity_detail = self.df[(self.df["Paper Short Name"] == proposal) & (self.df["Reviewer Name"] == reviewer)]["Anonymity Details"].to_string(index=False)
        handled_previously = self.df[(self.df["Paper Short Name"] == proposal) & (self.df["Reviewer Name"] == reviewer)]["Handled Previously"].to_string(index=False)
        return [summary, details, quetsion, anonymity, anonymity_detail, handled_previously]

    def wrap(self, string, lenght=35):
        return '\n'.join(textwrap.wrap(string, lenght))
    
    def get_reviews_in_order(self, reviewer, proposal, order):
        ret = []
        for i in range(len(order)):
            sent = self.df[(self.df["Paper Short Name"] == proposal) & (self.df["Reviewer Name"] == reviewer)][order[i]].to_string(index=False)
            ret.append(self.wrap(sent))
        return ret