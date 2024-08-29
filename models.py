from dataclasses import dataclass


@dataclass
class OnePage:
    """Class for each page."""
    source: str = None
    url: str = None
    imgurl: str = None
    plate: str = None
    verses: str = None
    transliteration: str = None
    filename: str = None


