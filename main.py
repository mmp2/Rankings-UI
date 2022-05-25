from GUI import GUI
from start_window import start_window

RATINGS_PATH = "dummy_ICML.xls"
RANKING = "ReviewerSubmissionComparisons.txt"
REVIEW_PATH = None
PROPOSAL_PATH = None
'''
RATING_PATHS = {
    "overall": OP_RATINGS_PATH,
    "Investigator": FQ_RATINGS_PATH,
    "Approach": OP_RATINGS_PATH,
    "Innovation": OP_RATINGS_PATH,
    "Significance": FQ_RATINGS_PATH,
}
'''
rating_to_attr = {
    "Bands": "Overall Score",
    "Box_Background_Color": "Relevance and Significance",
    "Width": "Novelty",
    "Dash": "Technical Quality",
    "Outline" : "Experimental Evaluation"
}


graph_attr = ["Bands", "Box_Background_Color", "Width", "Dash", "Outline"]
ratings = ["Overall Score", "Relevance and Significance", "Novelty", "Technical Quality", "Experimental Evaluation"]
rating_to_attr = start_window(graph_attr, ratings).start()

def main():
    #review_text = "This proposal is awesome."
    #example_review = Review(review=review_text)
    #ranking_path = input("Please Enter The Name of the Ranking File: ")
    #rankings = Ranking(ranking_path)
    instance = GUI(RANKING, RATINGS_PATH, REVIEW_PATH, PROPOSAL_PATH, rating_to_attr)
    #instance.createWindow()
    instance.show()

if __name__ == "__main__":
    main()