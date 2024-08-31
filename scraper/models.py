from dataclasses import dataclass, field


@dataclass
class PageRequest:
    status: str = None
    result: str = None
    url: str = None


@dataclass
class FullFolio:
    """Class for each folio"""
    doc_id: str = None
    title: list[str] = field(default_factory=list)
    contributor: list[str] = field(default_factory=list)
    relationship: str = None
    type: str = None
    language: list[str] = field(default_factory=list)
    description: list[str] = field(default_factory=list)
    rights: list[str] = field(default_factory=list)
    identifier: str = None
    source: str = None
    provenance: list[str] = field(default_factory=list)
    online_date: str = None
    transliteration_file: str = None
    urls: list[str] = field(default_factory=list)
    total_pages: int = None
    pages: list['OnePage'] = field(default_factory=list)



@dataclass
class OnePage:
    """Class for each page."""
    url: str = None
    imgurl: str = None
    plate: str = None
    verses: str = None
    transliteration: str = None
    imgpath: str = None
