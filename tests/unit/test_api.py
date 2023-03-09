from datetime import datetime
from unittest.mock import Mock, patch

from requests import Session

from readwise.api import Readwise, ReadwiseReader

readwise_client = Readwise('test_token')
readwise_reader = ReadwiseReader('test_token')


@patch.object(Session, 'request')
def test_paging(mock_get):
    page1 = Mock()
    page1.status_code = 200
    page1.json.return_value = {
        'next': 'https://example.com/api/v2/books/?page=2',
        'results': [
            {
                'id': 1,
                'title': 'Test Book',
            }
        ],
    }

    page2 = Mock()
    page2.status_code = 200
    page2.json.return_value = {
        'next': None,
        'results': [
            {
                'id': 2,
                'title': 'Test Book 2',
            }
        ],
    }

    mock_get.side_effect = [
        page1,
        page2,
    ]

    generator = readwise_client.get_pagination('test/')
    assert next(generator) == page1.json.return_value
    assert next(generator) == page2.json.return_value


@patch.object(Session, 'request')
def test_get_books_empty(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'results': [], 'next': None}
    highlights = list(readwise_client.get_books('articles'))
    assert len(highlights) == 0


@patch.object(Session, 'request')
def test_get_books(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'next': None,
        'results': [
            {
                'id': 1,
                'title': 'Test Book',
                'author': 'Test Author',
                'category': 'article',
                'source': 'Test Source',
                'num_highlights': 1,
                'last_highlight_at': '2020-01-01T00:00:00Z',
                'updated': '2020-01-01T00:00:00Z',
                'cover_image_url': 'https://example.com/image.jpg',
                'highlights_url': 'https://example.com/highlights',
                'source_url': 'https://example.com/source',
                'asin': 'test_asin',
                'tags': [
                    {'id': 1, 'name': 'test_tag'},
                    {'id': 2, 'name': 'test_tag_2'},
                ],
                'document_note': 'test_note',
            }
        ],
    }
    books = list(readwise_client.get_books('articles'))
    assert len(books) == 1
    assert books[0].id == 1
    assert books[0].title == 'Test Book'
    assert books[0].author == 'Test Author'
    assert books[0].category == 'article'
    assert books[0].source == 'Test Source'
    assert books[0].num_highlights == 1
    assert books[0].last_highlight_at == datetime.fromisoformat('2020-01-01T00:00:00Z')
    assert books[0].updated == datetime.fromisoformat('2020-01-01T00:00:00Z')
    assert books[0].cover_image_url == 'https://example.com/image.jpg'
    assert books[0].highlights_url == 'https://example.com/highlights'
    assert books[0].source_url == 'https://example.com/source'
    assert books[0].asin == 'test_asin'
    assert len(books[0].tags) == 2
    assert books[0].tags[0].id == 1
    assert books[0].tags[0].name == 'test_tag'
    assert books[0].tags[1].id == 2
    assert books[0].tags[1].name == 'test_tag_2'
    assert books[0].document_note == 'test_note'


@patch.object(Session, 'request')
def test_get_book_highlights_empty(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'next': None,
        'results': [],
    }
    highlights = list(readwise_client.get_book_highlights('1'))
    assert len(highlights) == 0


@patch.object(Session, 'request')
def test_get_book_highlights(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'next': None,
        'results': [
            {
                'id': 1,
                'text': 'Test Highlight',
                'note': 'Test Note',
                'location': 1,
                'location_type': 'page',
                'url': 'https://example.com/highlight',
                'color': 'yellow',
                'updated': '2020-01-01T00:00:00Z',
                'book_id': 1,
                'tags': [
                    {'id': 1, 'name': 'test_tag'},
                    {'id': 2, 'name': 'test_tag_2'},
                ],
            }
        ],
    }
    highlights = list(readwise_client.get_book_highlights('1'))
    assert len(highlights) == 1
    assert highlights[0].id == 1
    assert highlights[0].text == 'Test Highlight'
    assert highlights[0].note == 'Test Note'
    assert highlights[0].location == 1
    assert highlights[0].location_type == 'page'
    assert highlights[0].url == 'https://example.com/highlight'
    assert highlights[0].color == 'yellow'
    assert highlights[0].updated == datetime.fromisoformat('2020-01-01T00:00:00Z')
    assert highlights[0].book_id == 1
    assert len(highlights[0].tags) == 2
    assert highlights[0].tags[0].id == 1
    assert highlights[0].tags[0].name == 'test_tag'
    assert highlights[0].tags[1].id == 2
    assert highlights[0].tags[1].name == 'test_tag_2'
