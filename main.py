from Ranking import rankings
from GUI import GUI
from Review import review

OP_RATINGS_PATH = "OP_new.csv"
REVIEWS_PATH = "Reviews.csv"
FQ_RATINGS_PATH = "FQ Ratings.csv"
OVERALL_RANKINGS_PATH = "WXML dataset - OP Ranking.csv"

RATING_PATHS = {
    "OP": OP_RATINGS_PATH,
    "FQ": FQ_RATINGS_PATH
}

def main():
    #review_text = "This proposal is awesome."
    #example_review = Review(review=review_text)
    #ranking_path = input("Please Enter The Name of the Ranking File: ")
    #rankings = Ranking(ranking_path)
    instance = GUI(OVERALL_RANKINGS_PATH, REVIEWS_PATH, RATING_PATHS)
    #instance.createWindow()
    instance.show()

if __name__ == "__main__":
    main()