import sys
import os
path_to_package = os.path.join(os.path.abspath(os.getcwd()), "rankings_UI")
path_to_dir = os.path.abspath(os.getcwd())
sys.path.append(path_to_package)
sys.path.append(path_to_dir)
from GUI import GUI
from pre_process import process_into_dataframes, get_rankings
from Proposal import Proposals
from Ranking import Rankings
from Review import Reviews
from Reviewer import Reviewers

RANKING_PATH = os.path.join(os.path.abspath(os.getcwd()), "Examples/Paper Review Example/dummy_ranking.txt")
RATINGS_PATH = os.path.join(os.path.abspath(os.getcwd()), "Examples/Paper Review Example/dummy_rating.xls")
config_path = os.path.join(os.path.abspath(os.getcwd()), "Examples/Paper Review Example/config.toml")
titles = ["Summary", "Detailed Comments", "Questions for Author", "Anonymity", "Anonymity Details","Handled Previously"]

ratings, props, reviewers, reivews = process_into_dataframes(RATINGS_PATH, 15)
res, tie = get_rankings(RANKING_PATH, ratings)

ranks = Rankings(ratings, res, tie, list(ratings.columns[4:-2]), prop_col_name="Paper Short Name")
reviewers = Reviewers(reviewers)
reviews = Reviews(reivews, review_titles=titles, prop_colname="Paper Short Name")
props = Proposals(props)

def main():
    instance = GUI(ranks, reviews, reviews, props, config_path)
    instance.show()

if __name__ == "__main__":
    main()
