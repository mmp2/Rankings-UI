import pandas as pd

pd.options.display.max_colwidth = 1000

def distr_df(path, num_str=15):
    column_name = ["Paper ID", "Paper Title", "Reviewer Name", "Reviewer Email", "Reviewer Number",
                    "Created", "Last Modified", "Summary", "Detailed Comments", "Relevance and Significance", "Relevance and Significance-value",
                    "Novelty", "Novelty-value", "Technical Quality", "Technical Quality-value", "Experimental Evaluation", "Experimental Evaluation-value",
                    "Clarity", "Clarity-value", "Reproducibility", "Questions for Author", "Overall Score", "Overall Score-value",
                    "Confidence", "Confidence-value", "Confidential comments to SPC, AC, and Program Chairs", "Anonymity", "Anonymity Details", "Handled Previously", "Please acknowledge that you have read the author rebuttal"]
    df = pd.read_excel(path, skiprows=2, names=column_name)
    scores = df[['Reviewer Name', 'Reviewer Email','Paper Title', "Paper ID", "Overall Score-value", "Relevance and Significance-value", "Experimental Evaluation-value", "Novelty-value", "Technical Quality-value", "Clarity-value",
                "Confidence-value", "Reproducibility"]].copy()
    scores.rename(columns={"Overall Score-value": "Overall Score", 
                "Relevance and Significance-value": "Relevance and Significance",
                "Novelty-value": "Novelty",
                "Technical Quality-value": "Technical Quality",
                "Experimental Evaluation-value": "Experimental Evaluation",
                "Clarity-value": "Clarity",
                "Confidence-value": "Confidence"}, inplace=True)
    short_names = []
    for title in scores["Paper Title"].to_list():
        short_names.append(title[:num_str])
    scores["Paper Short Name"] = short_names
    props = df[['Reviewer Name', 'Reviewer Email','Paper Title', "Paper ID"]].copy()
    props["Paper Short Name"] = short_names
    reviewers = df[["Reviewer Name", "Reviewer Email", "Reviewer Number"]]
    reviews = df.copy()
    reviews["Paper Short Name"] = short_names
    return scores, props, reviewers, reviews

def get_prop_sname(id, scores):
    return scores.loc[scores["Paper ID"] == id, "Paper Short Name"].iloc[0]

def get_name(email, scores):
    return scores.loc[scores["Reviewer Email"] == email, "Reviewer Name"].iloc[0]

def rankings(path, scores):
    """
    returns a dictionary that indicates the true ranking for each reviewer
    and a dictionary that shows the ties that each reviewer gives.
    """
    result = {}
    tied = {}
    with open(path, encoding="utf-8") as r:
        lines = r.read().splitlines()
        i = 1
        while i != len(lines):
            if lines[i] != "":
                parts = lines[i].split("\t")
                if get_name(parts[0], scores) not in result:
                    result[get_name(parts[0], scores)] = []
                    tied[get_name(parts[0], scores)] = []
                left = get_prop_sname(int(parts[1]), scores)
                right = get_prop_sname(int(parts[3]), scores)
                if left in result[get_name(parts[0], scores)] and right not in result[get_name(parts[0], scores)]:
                    index = result[get_name(parts[0], scores)].index(left)
                    if parts[2] == "Comparable":
                        result[get_name(parts[0], scores)].insert(index, right)
                        exist = False
                        for i in range(len(tied[get_name(parts[0], scores)])):
                            if left in tied[get_name(parts[0], scores)][i]:
                                tied[get_name(parts[0], scores)][i].append(right)
                                exist = True
                                break
                            elif right in tied[get_name(parts[0], scores)][i]:
                                tied[get_name(parts[0], scores)][i].append(left)
                                exist = True
                                break
                        if not exist:
                            tied[get_name(parts[0], scores)].append([left, right])
                    else:
                        result[get_name(parts[0], scores)].insert(index+1, right)
                elif right in result[get_name(parts[0], scores)] and left not in result[get_name(parts[0], scores)]:
                    index = result[get_name(parts[0], scores)].index(right)
                    if parts[2] == "Comparable":
                        result[get_name(parts[0], scores)].insert(index, left)
                        exist = False
                        for i in range(len(tied[get_name(parts[0], scores)])):
                            if left in tied[get_name(parts[0], scores)][i]:
                                tied[get_name(parts[0], scores)][i].append(right)
                                exist = True
                                break
                            elif right in tied[get_name(parts[0], scores)][i]:
                                tied[get_name(parts[0], scores)][i].append(left)
                                exist = True
                                break
                        if not exist:
                            tied[get_name(parts[0], scores)].append([left, right])
                    else:
                        result[get_name(parts[0], scores)].insert(index, left)
                elif (len(result[get_name(parts[0], scores)]) != 0) and (right not in result[get_name(parts[0], scores)]) and (left not in result[get_name(parts[0], scores)]):
                    lines.append(lines[i])
                else:
                    result[get_name(parts[0], scores)].append(left)
                    result[get_name(parts[0], scores)].append(right)
                    if parts[2] == "Comparable":
                        exist = False
                        for i in range(len(tied[get_name(parts[0], scores)])):
                            if left in tied[get_name(parts[0], scores)][i]:
                                tied[get_name(parts[0], scores)][i].append(right)
                                exist = True
                                break
                            elif right in tied[get_name(parts[0], scores)][i]:
                                tied[get_name(parts[0], scores)][i].append(left)
                                exist = True
                                break
                        if not exist:
                            tied[get_name(parts[0], scores)].append([left, right])
            i += 1
    print(result, tied)
    return result, tied
    