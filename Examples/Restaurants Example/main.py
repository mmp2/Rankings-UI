from preprocess_rest import distr_df, rankings
from rankingTool.GUI import GUI
from rankingTool.Proposal import Proposals
from rankingTool.Ranking import Rankings
from rankingTool.Review import Reviews
from rankingTool.Reviewer import Reviewers
from rankingTool.Proposal import Proposals

other_paths = {
    "OS": "Examples/Restaurants Example/OS Ratings.csv",
    "FQ": "Examples/Restaurants Example/FQ Ratings.csv",
    "ST": "Examples/Restaurants Example/ST Ratings.csv",
    "WS": "Examples/Restaurants Example/WS Ratings.csv",
    "MK":"Examples/Restaurants Example/MK Ratings.csv"
}
ranking_path = "Examples/Restaurants Example/Ranking.csv"
OP_path = "Examples/Restaurants Example/OP_new.csv"
reviews_path ="Examples/Restaurants Example/Reviews.csv"
config_file =  "Examples/Restaurants Example/config_rest.toml"

ratings, props, reviewers, reivews = distr_df(ranking_path, OP_path, other_paths, reviews_path)
res, tie = rankings(ranking_path)
ranks = Rankings(ratings, res, tie, rating_names=list(ratings.columns[:6]), overall_col_name="OP")
reviewers = Reviewers(reviewers)
reviews = Reviews(reivews, ["One-word Rating"])
props = Proposals(props)


def main():
    instance = GUI(ranks, reviewers, reviews, props, config_file)
    instance.show()

if __name__ == "__main__":
    main()
