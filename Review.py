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
        return summary, details, quetsion, anonymity, anonymity_detail, handled_previously

    def wrap(self, string, lenght=35):
        return '\n'.join(textwrap.wrap(string, lenght))
    
    def get_reviews_in_order(self, reviewer, proposal, order):
        ret = []
        for i in range(len(order)):
            sent = self.df[(self.df["Paper Short Name"] == proposal) & (self.df["Reviewer Name"] == reviewer)][order[i]].to_string(index=False)
            ret.append(self.wrap(sent))
        return ret

'''
path = "dummy_ICML.xls"
column_name = ["Paper ID", "Paper Title", "Reviewer Name", "Reviewer Email", "Reviewer Number",
                "Created", "Last Modified", "Summary", "Detailed comments", "Relevance and Significance", "Relevance and Significance-value",
                "Novelty", "Novelty-value", "Technical quality", "Technical quality-value", "Experimental evaluation", "Experimental evaluation-value",
                "Clarity", "Clarity-value", "Reproducibility", "Questions for author", "Overall Score", "Overall Score-value",
                "Confidence", "Confidence-value", "Confidential comments to SPC, AC, and Program Chairs", "Anonymity", "Anonymity details", "Handled previously", "Please acknowledge that you have read the author rebuttal"]
df2 = pd.read_excel(path, header=2)
df = pd.read_excel(path, header=None, skiprows=3, names=column_name, dtype=str)

reviews = df.copy()
short_names = []
for title in df["Paper Title"].to_list():
    short_names.append(title[:15])
reviews["Paper Short Name"] = short_names
r = Reviews(reviews)
w = r.get_reviews_in_order("Dong Yin", "Paper2", ["Confidence"])
#print(w)
'''
