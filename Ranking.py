import pandas as pd
# I guess this class must be revised...
class Ranking:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path, header=0, index_col=0)

    def get_columns(self):
        return list(self.df.index)

    def get_num_rows(self):
        return len(self.df.columns)

    def get_vertical_rankings(self):
        columns = list(self.df.columns)
        rows = list(self.df.index)
        ret_list = [ [] for _ in range(len(columns)) ]
        for i in range(len(rows)):
            ordered_list = list(self.df.iloc[i].sort_values(ascending=True).index)
            for j in range(len(ordered_list)):
                ret_list[j].append(ordered_list[j])
        return ret_list
