from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReadwiseTag:
    '''Represents a Readwise tag.

    Attributes:
        id: The tag's ID.
        name: The tag's name.
    '''

    id: str
    name: str


@dataclass
class ReadwiseBook:
    '''
    Represents a Readwise book.

    Attributes:
        id: The book's ID.
        title: The book's title.
        author: The book's author.
        category: The book's category.
        source: The book's source.
        num_highlights: The number of highlights for the book.
        last_highlight_at: The date and time of the last highlight for the book.
        updated: The date and time the book was last updated.
        cover_image_url: The URL of the book's cover image.
        highlights_url: The URL of the book's highlights.
        source_url: The URL of the book's source.
        asin: The book's ASIN.
        tags: The book's tags.
        document_note: The book's document note.
    '''

    id: str
    title: str
    author: str
    category: str
    source: str
    num_highlights: int
    last_highlight_at: datetime | None
    updated: datetime
    cover_image_url: str
    highlights_url: str
    source_url: str
    asin: str
    tags: list[ReadwiseTag]
    document_note: str


@dataclass
class ReadwiseHighlight:
    '''
    Represents a Readwise highlight.

    Attributes:
        id: The highlight's ID.
        text: The highlight's text.
        note: The highlight's note.
        location: The highlight's location.
        location_type: The highlight's location type.
        url: The highlight's URL.
        color: The highlight's color.
        updated: The date and time the highlight was last updated.
        book_id: The ID of the book the highlight is from.
        tags: The highlight's tags.
    '''

    id: str
    text: str
    note: str
    location: int
    location_type: str
    url: str | None
    color: str
    updated: datetime
    book_id: str
    tags: list[ReadwiseTag]
