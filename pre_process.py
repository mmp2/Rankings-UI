import pandas as pd

def distr_df(path):
    num_str = 15

    df = pd.read_excel(path, header=2)

    scores = df[['Reviewer Name', 'Reviewer Email','Paper Title', "Paper ID", 'Q10 (Please provide an "overall score" for this submission.  - Value)', 'Q3 ([Relevance and Significance] (Is the subject matter important? Does the problem it tries to address have broad interests to the ICML audience or has impact in a certain special area? Is the proposed technique important, and will this work influence fu.1',
            "Q4 ([Novelty] (Is relation to prior work well-explained, does it present a new concept or idea, does it improve the existing methods, or extend the applications of existing practice?)   - Value)",
            "Q5 ( [Technical quality] (Is the approach technically sound. The claims and conclusions are supported by flawless arguments. Proofs are correct, formulas are correct, there are no hidden assumptions.) - Value)",
            'Q6 ([Experimental evaluation] (Are the experiments well designed, sufficient, clearly described? The experiments should demonstrate that the method works under the assumed conditions, probe a variety of aspects of the novel methods or ideas, not just the .1',
            "Q7 ([Clarity] (Is the paper well-organized and clearly written, should there be additional explanations or illustrations?)  - Value)"]].copy()

    scores.rename(columns={'Q10 (Please provide an "overall score" for this submission.  - Value)': "Overall Score", 
                'Q3 ([Relevance and Significance] (Is the subject matter important? Does the problem it tries to address have broad interests to the ICML audience or has impact in a certain special area? Is the proposed technique important, and will this work influence fu.1': "Relevance and Significance",
                "Q4 ([Novelty] (Is relation to prior work well-explained, does it present a new concept or idea, does it improve the existing methods, or extend the applications of existing practice?)   - Value)" : "Novelty",
                "Q5 ( [Technical quality] (Is the approach technically sound. The claims and conclusions are supported by flawless arguments. Proofs are correct, formulas are correct, there are no hidden assumptions.) - Value)": "Technical Quality",
                'Q6 ([Experimental evaluation] (Are the experiments well designed, sufficient, clearly described? The experiments should demonstrate that the method works under the assumed conditions, probe a variety of aspects of the novel methods or ideas, not just the .1': "Experimental Evaluation",
                "Q7 ([Clarity] (Is the paper well-organized and clearly written, should there be additional explanations or illustrations?)  - Value)": "Clarity"}, inplace=True)

    short_names = []
    for title in scores["Paper Title"].to_list():
        short_names.append(title[:num_str])
    scores["Paper Short Name"] = short_names

    props = df[['Reviewer Name', 'Reviewer Email','Paper Title', "Paper ID"]].copy()
    props["Paper Short Name"] = short_names


    reviewers = df[["Reviewer Name", "Reviewer Email", "Reviewer Number"]]


    reviews = df.copy()



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
