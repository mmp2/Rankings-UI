import pandas as pd
pd.options.display.max_colwidth = 1000
import textwrap
class Reviews:
    def __init__(self, df) -> None:
        self.df = df

    def get_all_review_sub(self, reviewer, proposal):
        review = self.df[reviewer, proposal].to_string(index=False)
        return [review]

    def wrap(self, string, lenght=35):
        return '\n'.join(textwrap.wrap(string, lenght))
    
    def get_reviews_in_order(self, reviewer, proposal, order):
        ret = []
        for i in range(len(order)):
            ret.append("No Information Now")
        return ret