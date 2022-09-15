from GUI import GUI
from pre_without_ties import distr_df, rankings
from prop_rest import Proposals
from ranking_rest import Rankings
from review_rest import Reviews
from reviewer_rest import Reviewers

RANKING_PATH = "dummy_ranking.txt"
RATINGS_PATH = "dummy_rating.xls"

other_paths = {
    "OS": "OS Ratings.csv",
    "FQ": "FQ Ratings.csv",
    "ST": "ST Ratings.csv",
    "WS": "WS Ratings.csv",
    "MK": "MK Ratings.csv"
}
ratings, props, reviewers, reivews = distr_df("Ranking.csv", "OP_new.csv", other_paths, "Reviews.csv")
res, tie = rankings("Ranking.csv")
ranks = Rankings(ratings, res, tie)
reviewers = Reviewers(reviewers)
reviews = Reviews(reivews)
props = Proposals(props)



def main():
    instance = GUI(ranks, reviews, reviews, props)
    instance.show()

if __name__ == "__main__":
    main()
