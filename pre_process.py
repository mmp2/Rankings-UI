import pandas as pd

pd.options.display.max_colwidth = 1000

def distr_df(path, num_str=15):

    column_name = ["Paper ID", "Paper Title", "Reviewer Name", "Reviewer Email", "Reviewer Number",
                    "Created", "Last Modified", "Summary", "Detailed Comments", "Relevance and Significance", "Relevance and Significance-value",
                    "Novelty", "Novelty-value", "Technical Quality", "Technical Quality-value", "Experimental Evaluation", "Experimental Evaluation-value",
                    "Clarity", "Clarity-value", "Reproducibility", "Questions for Author", "Overall Score", "Overall Score-value",
                    "Confidence", "Confidence-value", "Confidential comments to SPC, AC, and Program Chairs", "Anonymity", "Anonymity Details", "Handled Previously", "Please acknowledge that you have read the author rebuttal"]
    df = pd.read_excel(path, skiprows=2, names=column_name)

    #scores = df[['Reviewer Name', 'Reviewer Email','Paper Title', "Paper ID", 'Q10 (Please provide an "overall score" for this submission.  - Value)', 'Q3 ([Relevance and Significance] (Is the subject matter important? Does the problem it tries to address have broad interests to the ICML audience or has impact in a certain special area? Is the proposed technique important, and will this work influence fu.1',
            #"Q4 ([Novelty] (Is relation to prior work well-explained, does it present a new concept or idea, does it improve the existing methods, or extend the applications of existing practice?)   - Value)",
            #"Q5 ( [Technical quality] (Is the approach technically sound. The claims and conclusions are supported by flawless arguments. Proofs are correct, formulas are correct, there are no hidden assumptions.) - Value)",
            #'Q6 ([Experimental evaluation] (Are the experiments well designed, sufficient, clearly described? The experiments should demonstrate that the method works under the assumed conditions, probe a variety of aspects of the novel methods or ideas, not just the .1',
            #"Q7 ([Clarity] (Is the paper well-organized and clearly written, should there be additional explanations or illustrations?)  - Value)"]].copy()
    scores = df[['Reviewer Name', 'Reviewer Email','Paper Title', "Paper ID", "Overall Score-value", "Relevance and Significance-value", "Experimental Evaluation-value", "Novelty-value", "Technical Quality-value", "Clarity-value",
                "Confidence-value"]].copy()
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



    '''
        reviews.rename(columns={
            "Q1 ([Summary] Please summarize the main claims/contributions of the paper in your own words (1-2 sentences or paragraphs). )": "Q1",
            "Q2 ([Detailed comments] Describe the strengths and weaknesses of the work, with respect to the following criteria: soundness of the claims (theoretical grounding, empirical evaluation), significance and novelty of the contribution, relation with prior wor": "Q2",
            "Q3 ([Relevance and Significance] (Is the subject matter important? Does the problem it tries to address have broad interests to the ICML audience or has impact in a certain special area? Is the proposed technique important, and will this work influence fu":"Q3",
            "Q4 ([Novelty] (Is relation to prior work well-explained, does it present a new concept or idea, does it improve the existing methods, or extend the applications of existing practice?)  )": "Q4",
            "Q5 ( [Technical quality] (Is the approach technically sound. The claims and conclusions are supported by flawless arguments. Proofs are correct, formulas are correct, there are no hidden assumptions.))": "Q5",
            "Q6 ([Experimental evaluation] (Are the experiments well designed, sufficient, clearly described? The experiments should demonstrate that the method works under the assumed conditions, probe a variety of aspects of the novel methods or ideas, not just the ": "Q6",
            'Q7 ([Clarity] (Is the paper well-organized and clearly written, should there be additional explanations or illustrations?) )':"Q7",
            'Q8 ([Reproducibility] (are there enough details to reproduce the major results of this work?) )': "Q8",
            'Q9 ([Questions for authors] Please provide questions for authors to address during the author feedback period. (Optional, to help authors focus their response to your review.))':"Q9",
            'Q10 (Please provide an "overall score" for this submission. )':"Q10",
            'Q12 ( [Confidential comments to SPC, AC, and Program Chairs] (including potential ethical concerns) )':"Q12",

        })
    '''
