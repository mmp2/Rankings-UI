from GUI import GUI
from pre_process import distr_df, rankings
from Proposal import Proposals
from Ranking import Rankings
from Review import Reviews
from Reviewer import Reviewers

RANKING_PATH = "dummy_ranking.txt"
RATINGS_PATH = "dummy_rating.xls"


ratings, props, reviewers, reivews = distr_df(RATINGS_PATH, 15)
res, tie = rankings(RANKING_PATH, ratings)
ranks = Rankings(ratings, res, tie)
reviewers = Reviewers(reviewers)
reviews = Reviews(reivews)
props = Proposals(props)



def main():
    instance = GUI(ranks, reviews, reviews, props)
    instance.show()

if __name__ == "__main__":
    main()