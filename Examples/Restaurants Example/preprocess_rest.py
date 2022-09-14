import numpy as np
import pandas as pd

def distr_df(ranking_path, op_path, other_paths, review_path, num_str=15):
    df = pd.read_csv(ranking_path, header=0, index_col=0)
    rating_names = list(other_paths.keys())
    score = pd.DataFrame(columns=rating_names)
    score["Reviewer Name"] = 0
    score["Proposal Name"] = 0
    score["OP"] = 0
    op = pd.read_csv(op_path, header=0, index_col=0)
    ratings = {}
    for rate_name in other_paths.keys():
        ratings[rate_name] = pd.read_csv(other_paths[rate_name], header=0, index_col=0)
    for rest_name in list(df.columns):
        for review_name in list(df.index):
            dict = {"OS": ratings["OS"].loc[review_name][rest_name], 
                    "FQ": ratings["FQ"].loc[review_name][rest_name],
                    "ST": ratings["ST"].loc[review_name][rest_name],
                    "WS": ratings["WS"].loc[review_name][rest_name],
                    "MK": ratings["MK"].loc[review_name][rest_name], 
                    "Reviewer Name": review_name, 
                    "Proposal Name": rest_name, 
                    "OP": op.at[review_name, rest_name]}
            score = score.append(dict, ignore_index = True)
    short_names = []
    for title in score["Proposal Name"].to_list():
        short_names.append(title[:num_str])
    score["Proposal Name"] = short_names
    props = score[["Reviewer Name", "Proposal Name"]].copy()
    reviewers = score[["Reviewer Name"]].copy()
    reviews_df = pd.read_csv(review_path, header=0, index_col=0)
    return score, props, reviewers, reviews_df

def rankings(path):
    df = pd.read_csv(path, header=0, index_col=0)
    rows = list(df.index)
    ret = {}
    for i in range(len(rows)):
        ordered_list = list(df.iloc[i].sort_values(ascending=True).index)
        ret[rows[i]] = ordered_list
    return ret, None

