import csv
from collections.abc import Sequence
from typing import Any


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


def write_csv(file_name: str, lines: Sequence[Any]):
    # ensure argument validity
    if len(lines) == 0:
        raise ValueError("Cannot write empty database file")
    first_type = type(lines[0])
    if not all(isinstance(line, first_type) for line in lines):
        raise ValueError("All line objects must be of same type")

    # write file
    with open(file_name, 'w', newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(lines[0].__dict__.keys()), delimiter=";")
        writer.writeheader()
        for line in lines:
            writer.writerow(line.__dict__)
