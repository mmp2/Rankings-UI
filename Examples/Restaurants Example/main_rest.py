from GUI import GUI
from preprocess_rest import distr_df, rankings
from Proposal import Proposals
from Ranking import Rankings
from Review import Reviews
from Reviewer import Reviewers
from Proposal import Proposals

other_paths = {
    "OS": "OS Ratings.csv",
    "FQ": "FQ Ratings.csv",
    "ST": "ST Ratings.csv",
    "WS": "WS Ratings.csv",
    "MK": "MK Ratings.csv"
}
ratings, props, reviewers, reivews = distr_df("Ranking.csv", "OP_new.csv", other_paths, "Reviews.csv")
res, tie = rankings("Ranking.csv")
ranks = Rankings(ratings, res, tie, rating_names=list(ratings.columns[:6]), overall_col_name="OP")
reviewers = Reviewers(reviewers)
reviews = Reviews(reivews, ["One-word Rating"])
props = Proposals(props)


def main():
    instance = GUI(ranks, reviewers, reviews, props, "config_rest.toml")
    instance.show()

if __name__ == "__main__":
    main()