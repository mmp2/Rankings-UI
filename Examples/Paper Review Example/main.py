from pre_process import process_into_dataframes, get_rankings
from rankingTool.GUI import GUI
from rankingTool.Proposal import Proposals
from rankingTool.Ranking import Rankings
from rankingTool.Review import Reviews
from rankingTool.Reviewer import Reviewers
from rankingTool.Proposal import Proposals

RANKING_PATH = "Examples/Paper Review Example/dummy_ranking.txt"
RATINGS_PATH =  "Examples/Paper Review Example/dummy_rating.xls"
config_path = "Examples/Paper Review Example/config.toml"
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
