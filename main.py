from Ranking import rankings
from GUI import GUI
from Review import review

OP_RATINGS_PATH = "OP_new.csv"
REVIEWS_PATH = "Reviews.csv"
FQ_RATINGS_PATH = "FQ Ratings.csv"
OVERALL_RANKINGS_PATH = "WXML dataset - OP Ranking.csv"
OS_RATINGS_PATH = "OS Ratings.csv"
ST_RATINGS_PATH = "ST Ratings.csv"


PROPOSAL_PATH = None

RATING_PATHS = {
    "overall": OP_RATINGS_PATH,
    "Investigator": FQ_RATINGS_PATH,
    "Approach": OP_RATINGS_PATH,
    "Innovation": OP_RATINGS_PATH,
    "Significance": FQ_RATINGS_PATH,
}

rating_to_attr = {
    "bands": "Overall_Merit",
    "box_bgc": "Investigator",
    "x_coord": "Approach",
    "dash": "Innovation",
    "outline" : "Significance"
}

def main():
    #review_text = "This proposal is awesome."
    #example_review = Review(review=review_text)
    #ranking_path = input("Please Enter The Name of the Ranking File: ")
    #rankings = Ranking(ranking_path)
    instance = GUI(OVERALL_RANKINGS_PATH, REVIEWS_PATH, RATING_PATHS, PROPOSAL_PATH, rating_to_attr)
    #instance.createWindow()
    instance.show()

if __name__ == "__main__":
    main()