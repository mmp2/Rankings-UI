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


