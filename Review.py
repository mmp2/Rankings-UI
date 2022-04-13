
class Review:
    def __init__(self, reviewer=None, proposal=None, review=None) -> None:
        """
        reviewers: a string of the name of reviewer
        reviews: a string of review
        proposal: a string of proposal
        """
        self.reviewer = reviewer
        self.proposal = proposal
        self.text = review

    def get_review(self):
        return self.text
    