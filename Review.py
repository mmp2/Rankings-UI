import pandas as pd

class Reviews:
    def __init__(self, df) -> None:
        self.df = df


    def get_review(self, reviewer, proposal):
        return self.df.loc[reviewer][proposal]
    