import pandas as pd
import numpy as np


class rankings:
    def __init__(self, ranking_path, score_path):

        df = pd.read_excel(score_path, header=2)

        self.scores = df[['Reviewer Email','Paper ID','Q10 (Please provide an "overall score" for this submission.  - Value)', 'Q3 ([Relevance and Significance] (Is the subject matter important? Does the problem it tries to address have broad interests to the ICML audience or has impact in a certain special area? Is the proposed technique important, and will this work influence fu.1',
            "Q4 ([Novelty] (Is relation to prior work well-explained, does it present a new concept or idea, does it improve the existing methods, or extend the applications of existing practice?)   - Value)",
            "Q5 ( [Technical quality] (Is the approach technically sound. The claims and conclusions are supported by flawless arguments. Proofs are correct, formulas are correct, there are no hidden assumptions.) - Value)",
            'Q6 ([Experimental evaluation] (Are the experiments well designed, sufficient, clearly described? The experiments should demonstrate that the method works under the assumed conditions, probe a variety of aspects of the novel methods or ideas, not just the .1',
            "Q7 ([Clarity] (Is the paper well-organized and clearly written, should there be additional explanations or illustrations?)  - Value)"]].copy()

        self.scores.rename(columns={'Q10 (Please provide an "overall score" for this submission.  - Value)': "Overall Score", 
                'Q3 ([Relevance and Significance] (Is the subject matter important? Does the problem it tries to address have broad interests to the ICML audience or has impact in a certain special area? Is the proposed technique important, and will this work influence fu.1': "Relevance and Significance",
                "Q4 ([Novelty] (Is relation to prior work well-explained, does it present a new concept or idea, does it improve the existing methods, or extend the applications of existing practice?)   - Value)" : "Novelty",
                "Q5 ( [Technical quality] (Is the approach technically sound. The claims and conclusions are supported by flawless arguments. Proofs are correct, formulas are correct, there are no hidden assumptions.) - Value)": "Technical Quality",
                'Q6 ([Experimental evaluation] (Are the experiments well designed, sufficient, clearly described? The experiments should demonstrate that the method works under the assumed conditions, probe a variety of aspects of the novel methods or ideas, not just the .1': "Experimental Evaluation",
                "Q7 ([Clarity] (Is the paper well-organized and clearly written, should there be additional explanations or illustrations?)  - Value)": "Clarity"}, inplace=True)

        self.ranking = self.rankings(ranking_path)
        self.rating_names = self.scores.columns[2:]

        self.index = list(self.scores["Reviewer Email"].unique())
        self.columns = list(self.scores["Paper ID"].unique())

    def get_rating_df(self, rat_name):
        df = pd.DataFrame(index=self.scores["Reviewer Email"].unique(), columns=self.scores["Paper ID"].unique())
        for index in self.index:
            for column in self.columns:
                df.loc[index][column] = self.get_sub_rating(rat_name, index, column)
        return df

    def rankings(self, path):
        result = {}
        with open(path, encoding="utf-8") as r:
            lines = r.read().splitlines()
            i = 1
            while i != len(lines):
                if lines[i] != "":
                    parts = lines[i].split("\t")
                    if parts[0] not in result:
                        result[parts[0]] = []
                    left = parts[1]
                    right = parts[3]
                    if left in result[parts[0]] and right not in result[parts[0]]:
                        index = result[parts[0]].index(left)
                        if parts[2] == "Comparable":
                            result[parts[0]].insert(index, right)
                        else:
                            result[parts[0]].insert(index+1, right)
                    elif right in result[parts[0]] and left not in result[parts[0]]:
                        index = result[parts[0]].index(right)
                        if parts[2] == "Comparable":
                            result[parts[0]].insert(index, left)
                        else:
                            result[parts[0]].insert(index, left)
                    elif (len(result[parts[0]]) != 0) and (right not in result[parts[0]]) and (left not in result[parts[0]]):
                        lines.append(lines[i])
                    else:
                        result[parts[0]].append(left)
                        result[parts[0]].append(right)
                i += 1
        return result
    
    def get_sub_rating(self, rat_name, reviewer, prop):
        l = self.scores.loc[(self.scores["Reviewer Email"] == reviewer) & (self.scores["Paper ID"] == prop), rat_name].tolist()
        if l:
            return l[0]
        else:
            return np.nan
        #return self.ratings[rat_name].loc[reviewer, prop]

    def get_all_sub_ratings(self):
        return self.rating_names

    def get_columns(self):
        return list(self.index)

    def get_all_rankings(self):
        ret = []
        for key in self.ranking.keys():
          ret.append(self.ranking[key])  
        return ret


    def get_op_rankings(self):
        df_op = self.get_rating_df("Overall Score")
        ret = {}
        rows = list(self.index)
        props = list(self.columns)
        maxi = 0
        for reviewer in rows:
            ret[reviewer] = {}
            for prop in props:
                rate = df_op.loc[reviewer, prop]
                if not np.isnan(rate):
                    if rate not in ret[reviewer]:
                        ret[reviewer][rate] = [prop]
                    else:
                        ret[reviewer][rate].append(prop)
                        if len(ret[reviewer][rate]) > maxi:
                            maxi = len(ret[reviewer][rate])
        return ret, maxi


''''
RATINGS_PATH = "dummy_ICML.xls"
RANKING = "ReviewerSubmissionComparisons.txt"

instance = rankings(RANKING, RATINGS_PATH)
#print(instance.get_op_rankings())
print(instance.rankings)
'''