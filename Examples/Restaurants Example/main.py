import sys
import os
path_to_package = os.path.join(os.path.abspath(os.getcwd()), "rankings_UI")
path_to_dir = os.path.abspath(os.getcwd())
sys.path.append(path_to_package)
sys.path.append(path_to_dir)
from GUI import GUI
from preprocess_rest import distr_df, rankings
from Proposal import Proposals
from Ranking import Rankings
from Review import Reviews
from Reviewer import Reviewers
from Proposal import Proposals

other_paths = {
    "OS": os.path.join(os.path.abspath(os.getcwd()), "Examples/Restaurants Example/OS Ratings.csv"),
    "FQ": os.path.join(os.path.abspath(os.getcwd()), "Examples/Restaurants Example/FQ Ratings.csv"),
    "ST": os.path.join(os.path.abspath(os.getcwd()), "Examples/Restaurants Example/ST Ratings.csv"),
    "WS": os.path.join(os.path.abspath(os.getcwd()), "Examples/Restaurants Example/WS Ratings.csv"),
    "MK": os.path.join(os.path.abspath(os.getcwd()), "Examples/Restaurants Example/MK Ratings.csv")
}
ranking_path = os.path.join(os.path.abspath(os.getcwd()), "Examples/Restaurants Example/Ranking.csv")
OP_path = os.path.join(os.path.abspath(os.getcwd()), "Examples/Restaurants Example/OP_new.csv")
reviews_path = os.path.join(os.path.abspath(os.getcwd()), "Examples/Restaurants Example/Reviews.csv")
config_file = os.path.join(os.path.abspath(os.getcwd()), "Examples/Restaurants Example/config_rest.toml")

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
