import pandas as pd
import textwrap
class Reviews:
    def __init__(self, df) -> None:
        self.df = df


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
