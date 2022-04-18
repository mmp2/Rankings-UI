import pandas as pd
class review:
    def __init__(self, file_path) -> None:
        """
        """
        self.df = pd.read_csv(file_path, header=0, index_col=0)
        #self.text = review

    def get_review(self, reviewer, proposal):
        return self.df.loc[reviewer][proposal]
    