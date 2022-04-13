
class Reviewer:
    def __init__(self, name, proposals, reviews, rankings) -> None:
        """
        name: the name of current reviewer
        proposals: a list of proposals
        reviews: a list of reviews each of which is written for the corresponding proposal
        with the same index as in the proposals list.
        rankings: a list of strings of proposals in the ascending order of the rankings.
        """
        #I think best to have reviews in arbitrary order (each review has a pointer to proposal); then ranking is w.r.t to reviews list.
        #This is because sometimes a reviewer does not enter all reviews.
        # alternatively, we can keep a master list of all proposals, and all rankings should be w.r.t to this list (Note that reviewers usuaally don't review all proposals, for various reasons, so we must allow for incomplete lists)
        self.name = name
        self.proposals = proposals
        self.reviews = reviews
        self.rankings = rankings  # should be a single ranking, could be a list of *reviews

        # remember: same set of restaurants(=proposals), each Participant(=reviewer) outputs a single ranking
    def get_reviews(self):
        return self.reviews
