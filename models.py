from dataclasses import dataclass, field


@dataclass
class PageRequest:
    status: str = None
    result: str = None
    url: str = None


@dataclass
class FullFolio:
    """Class for each folio"""
    source: str = None
    baseurl: str = None
    transliteration_file: str = None
    identifier: str = None
    urls: list[str] = field(default_factory=list)
    total_pages: int = None
    pages: list['OnePage'] = field(default_factory=list)



@dataclass
class OnePage(FullFolio):
    """Class for each page."""
    source: str = None
    url: str = None
    imgurl: str = None
    plate: str = None
    verses: str = None
    transliteration: str = None
    filename: str = None
