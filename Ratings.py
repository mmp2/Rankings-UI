import pandas as pd

class ratings:
    def __init__(self, file_path) -> None:
        self.df = pd.read_csv(file_path, header=0, index_col=0)
        
    def get_rating(self, reviewer, proposal):
        return self.df.loc[reviewer][proposal]