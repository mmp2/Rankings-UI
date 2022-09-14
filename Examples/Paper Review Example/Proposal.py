import pandas as pd

class Proposals:
    def __init__(self, df) -> None:
        self.df = df

    def get_short_name(self, title):
        num_str = 15     # The number of strings in the short name of the title
        return title[:num_str]
    
    def get_full_title(self, id):
        return self.df.loc[self.df["Paper ID"] == id, "Paper Title"].iloc[0]
    
    def get_detail(self, short_name):
        return "No Information Now."
    
    def get_time_created(self, id):
        return self.df.loc[self.df["Paper ID"] == id, "Created"].iloc[0]
    
    def get_last_mod(self, id):
        return self.df.loc[self.df["Paper ID"] == id, "Last Modified"].iloc[0]