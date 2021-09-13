
class Unknown:
    """
    Simple class with a single instance representing an unknown value in the database
    """

    def __str__(self):
        return "unknown"

    def __repr__(self):
        return "UNKNOWN"

    def __eq__(self, other):
        return isinstance(other, Unknown)

    def __hash__(self):
        return hash(Unknown)


UNKNOWN = Unknown()
