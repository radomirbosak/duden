"""
Module containing the base class for duden pages
"""


class DudenPage:
    """
    Represents a general duden page
    """

    # pylint: disable=too-few-public-methods
    def __init__(self, soup):
        self.soup = soup

    def division(self, title):
        """Find general page division by its title"""
        for division in self.soup.find_all("div", class_="division"):
            div_title = division.find("h2", class_="division__title")
            if div_title and div_title.text == title:
                return division
        raise KeyError(title)
