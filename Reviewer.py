import pandas as pd

class Reviewers:
    def __init__(self, df) -> None:
        self.df = df

    def get_name(self, email):
        return self.df.loc[self.df["Reviewer Email"] == email, "Reviewer Name"].iloc[0]
    

    def get_number(self, email):
        return self.df.loc[self.df["Reviewer Email"] == email, "Reviewer Number"].iloc[0]