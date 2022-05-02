
class proposal:
    def __init__(self, proposal_path) -> None:
        """
        Not implemented yet, since not sure about the input format of the proposals.
        
        """
        self.props: list() = None
        self.short_names: dict() = None
        self.details: dict() = None

    def short_name(self, prop):
        return self.short_names[prop]

    def get_detail(self, prop):
        return self.details[prop]