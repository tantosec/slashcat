import re


class MatchesRegex:
    def __init__(self, rgx):
        self.rgx = re.compile(rgx)

    def __repr__(self):
        return repr(self.rgx)

    def __eq__(self, other):
        return len(self.rgx.findall(str(other))) > 0
