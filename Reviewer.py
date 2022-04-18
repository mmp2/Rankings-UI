class Reviewers:
    def __init__(self, name, proposals, reviews, rankings) -> None:
        """
        name: the name of current reviewer
        proposals: a list of proposals
        reviews: a list of reviews each of which is written for the corresponding proposal
        with the same index as in the proposals list.
        rankings: a list of strings of proposals in the ascending order of the rankings.
        """
        self.name = name
        self.proposals = proposals
        self.reviews = reviews
        self.rankings = rankings

    def get_reviews(self):
        return self.reviews