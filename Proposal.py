
class Proposal:
    def __init__(self, name, reviewers, reviews) -> None:
        """
        reviewers: a list of reviewers
        reviews: a list of reviews each of which is written by the corresponding reviewer 
        with the same index as in the reviewers list.
        name: the name of current proposal
        """
        self.reviewer = reviewers
        self.name = name
        self.review = reviews

    def get_name(self):
        return self.name