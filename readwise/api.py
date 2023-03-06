import logging
from datetime import datetime
from time import sleep
from typing import Any, Generator, Literal

import requests
from backoff import expo, on_exception
from ratelimit import RateLimitException, limits, sleep_and_retry

from readwise.models import ReadwiseBook, ReadwiseHighlight, ReadwiseTag


class ReadwiseRateLimitException(Exception):
    '''Raised when the Readwise API rate limit is exceeded.'''

    pass


class ReadwiseClient:
    def __init__(
        self,
        token: str,
    ):
        '''
        Initialize a ReadwiseClient.

        Documentation for the Readwise API can be found here:
        https://readwise.io/api_deets

        Args:
            token: Readwise API token
        '''
        self.token = token
        self.url = 'https://readwise.io/api/v2'

    @property
    def _session(self) -> requests.Session:
        '''
        Return a requests.Session object with the Readwise API token set as an
        Authorization header.
        '''
        session = requests.Session()
        session.headers.update(
            {
                'Accept': 'application/json',
                'Authorization': f'Token {self.token}',
            }
        )
        return session

    @on_exception(expo, RateLimitException, max_tries=8)
    @sleep_and_retry
    @limits(calls=240, period=60)
    def _request(
        self, method: str, endpoint: str, params: dict = {}, data: dict = {}
    ) -> requests.Response:
        '''
        Make a request to the Readwise API.

        The Readwise API has a rate limit of 240 requests per minute. This
        method will raise a ReadwiseRateLimitException if the rate limit is
        exceeded.

        The Exception will be raised after 8 retries with exponential backoff.

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body

        Returns:
            requests.Response
        '''
        url = self.url + endpoint
        logging.debug(f'Calling "{method}" on "{url}" with params: {params}')
        response = self._session.request(method, url, params=params, json=data)
        while response.status_code == 429:
            seconds = int(response.headers['Retry-After'])
            logging.warning(f'Rate limited by Readwise, retrying in {seconds} seconds')
            sleep(seconds)
            response = self._session.request(method, url, params=params, data=data)
        response.raise_for_status()
        return response

    def get(self, endpoint: str, params: dict = {}) -> requests.Response:
        '''
        Make a GET request to the Readwise API.

        Examples:
            >>> client.get('/highlights/')

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            requests.Response
        '''
        logging.debug(f'Getting "{endpoint}" with params: {params}')
        return self._request('GET', endpoint, params=params)

    @on_exception(expo, RateLimitException, max_tries=8)
    @sleep_and_retry
    @limits(calls=20, period=60)
    def get_with_limit_20(self, endpoint: str, params: dict = {}) -> requests.Response:
        '''
        Get a response from the Readwise API with a rate limit of 20 requests
        per minute.

        The rate limit of 20 requests per minute needs to be used at the
        endpoints /highlights/ and /books/ because they return a lot of data.

        Args:
            endpoint: API endpoint
            params: Query parameters
        Returns:
            requests.Response
        '''
        return self.get(endpoint, params)

    def post(self, endpoint: str, data: dict = {}) -> requests.Response:
        '''
        Make a POST request to the Readwise API.

        Examples:
            >>> client.post('/highlights/', {'highlights': [{'text': 'foo'}]})

        Args:
            endpoint: API endpoint
            data: Request body

        Returns:
            requests.Response
        '''
        url = self.url + endpoint
        logging.debug(f'Posting "{url}" with data: {data}')
        response = self._request('POST', endpoint, data=data)
        response.raise_for_status()
        return response

    def delete(self, endpoint: str) -> requests.Response:
        '''
        Make a DELETE request to the Readwise API.

        Examples:
            >>> client.delete('/highlights/1234')

        Args:
            endpoint: API endpoint

        Returns:
            requests.Response
        '''
        logging.debug(f'Deleting "{endpoint}"')
        return self._request('DELETE', endpoint)

    def get_books(
        self, category: Literal['articles', 'books', 'tweets', 'podcasts']
    ) -> Generator[ReadwiseBook, None, None]:
        '''
        Get all Readwise books.

        Args:
            category: Book category

        Returns:
            A generator of ReadwiseBook objects
        '''
        page = 1
        page_size = 1000
        while True:
            data = self.get_with_limit_20(
                '/books',
                {'page': page, 'page_size': page_size, 'category': category},
            ).json()

            for book in data['results']:
                yield ReadwiseBook(
                    id=book['id'],
                    title=book['title'],
                    author=book['author'],
                    category=book['category'],
                    source=book['source'],
                    num_highlights=book['num_highlights'],
                    last_highlight_at=datetime.fromisoformat(book['last_highlight_at']),
                    updated=datetime.fromisoformat(book['updated']),
                    cover_image_url=book['cover_image_url'],
                    highlights_url=book['highlights_url'],
                    source_url=book['source_url'],
                    asin=book['asin'],
                    tags=[
                        ReadwiseTag(id=tag['id'], name=tag['name'])
                        for tag in book['tags']
                    ],
                    document_note=book['document_note'],
                )

            if not data['next']:
                break
            page += 1

    def get_book_highlights(
        self, book_id: str
    ) -> Generator[ReadwiseHighlight, None, None]:
        '''
        Get all highlights for a Readwise book.

        Args:
            book_id: Readwise book ID

        Returns:
            A generator of ReadwiseHighlight objects
        '''
        page = 1
        page_size = 1000
        while True:
            data = self.get_with_limit_20(
                '/highlights',
                {'page': page, 'page_size': page_size, 'book_id': book_id},
            ).json()
            for highlight in data['results']:
                yield ReadwiseHighlight(
                    id=highlight['id'],
                    text=highlight['text'],
                    note=highlight['note'],
                    location=highlight['location'],
                    location_type=highlight['location_type'],
                    url=highlight['url'],
                    color=highlight['color'],
                    updated=datetime.fromisoformat(highlight['updated']),
                    book_id=highlight['book_id'],
                    tags=[
                        ReadwiseTag(id=tag['id'], name=tag['name'])
                        for tag in highlight['tags']
                    ],
                )

            if not data['next']:
                break
            page += 1

    def create_highlight(
        self,
        text: str,
        title: str,
        author: str | None = None,
        highlighted_at: datetime | None = None,
        source_url: str | None = None,
        category: str = 'articles',
        note: str | None = None,
    ):
        '''
        Create a Readwise highlight.

        Args:
            text: Highlight text
            title: Book title
            author: Book author
            highlighted_at: Date and time the highlight was created
            source_url: URL of the book
            category: Book category
            note: Highlight note
        '''
        payload = {'text': text, 'title': title, 'category': category}
        if author:
            payload['author'] = author
        if highlighted_at:
            payload['highlighted_at'] = highlighted_at.isoformat()
        if source_url:
            payload['source_url'] = source_url
        if note:
            payload['note'] = note

        self.post('/highlights/', {'highlights': [payload]})

    def get_book_tags(self, book_id: str) -> Generator[ReadwiseTag, None, None]:
        '''
        Get all tags for a Readwise book.

        Args:
            book_id: Readwise book ID

        Returns:
            A generator of ReadwiseTag objects
        '''
        page = 1
        page_size = 1000
        data = self.get(
            f'/books/{book_id}/tags',
            {'page': page, 'page_size': page_size, 'book_id': book_id},
        ).json()

        for tag in data:
            yield ReadwiseTag(tag['id'], tag['name'])

    def add_tag(self, book_id: str, tag: str):
        '''
        Add a tag to a Readwise book.

        Args:
            book_id: Readwise book ID
            tag: Tag name

        Returns:
            requests.Response
        '''
        logging.debug(f'Adding tag "{tag}" to book "{book_id}"')
        payload = {'name': tag}
        self.post(f'/books/{book_id}/tags/', payload)

    def delete_tag(self, book_id: str, tag_id: str):
        '''
        Delete a tag from a Readwise book.

        Args:
            book_id: Readwise book ID

        Returns:
            requests.Response
        '''
        logging.debug(f'Deleting tag "{tag_id}"')
        self.delete(f'/books/{book_id}/tags/{tag_id}')


class ReadwiseReaderClient:
    def __init__(
        self,
        token: str,
    ):
        '''
        Readwise Reader Connector.

        Documentation for the Readwise Reader API can be found here:
        https://readwise.io/reader_api

        Args:
            token: Readwise Reader Connector token
        '''
        self.token = token
        self.url = 'https://readwise.io/api/v3'

    @property
    def _session(self) -> requests.Session:
        '''
        Session object for making requests.
        The headers are set to include the token.
        '''
        session = requests.Session()
        session.headers.update(
            {
                'Accept': 'application/json',
                'Authorization': f'Token {self.token}',
            }
        )
        return session

    @on_exception(expo, RateLimitException, max_tries=8)
    @sleep_and_retry
    @limits(calls=20, period=60)
    def _request(
        self, method: str, endpoint: str, params: dict = {}, data: dict = {}
    ) -> requests.Response:
        '''
        Make a request to the Readwise Reader API.
        The request is rate limited to 20 calls per minute.

        Args:
            method: HTTP method
            endpoint: API endpoints
            params: Query parameters
            data: Request body

        Returns:
            requests.Response
        '''
        url = self.url + endpoint
        logging.debug(f'Calling "{method}" on "{url}" with params: {params}')
        response = self._session.request(method, url, params=params, json=data)
        while response.status_code == 429:
            seconds = int(response.headers['Retry-After'])
            logging.warning(f'Rate limited by Readwise, retrying in {seconds} seconds')
            sleep(seconds)
            response = self._session.request(method, url, params=params, data=data)
        response.raise_for_status()
        return response

    def get(self, endpoint: str, params: dict = {}) -> requests.Response:
        '''
        Make a GET request to the Readwise Reader API.

        Args:
            endpoint: API endpoints
            params: Query parameters

        Returns:
            requests.Response
        '''
        logging.debug(f'Getting "{endpoint}" with params: {params}')
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: dict = {}) -> requests.Response:
        '''
        Make a POST request to the Readwise Reader API.

        Args:
            endpoint: API endpoints
            data: Request body

        Returns:
            requests.Response
        '''
        url = self.url + endpoint
        logging.debug(f'Posting "{url}" with data: {data}')
        response = self._request('POST', endpoint, data=data)
        response.raise_for_status()
        return response

    def create_document(
        self,
        url: str,
        html: str | None = None,
        should_clean_html: bool | None = None,
        title: str | None = None,
        author: str | None = None,
        summary: str | None = None,
        published_at: datetime | None = None,
        image_url: str | None = None,
        location: Literal['new', 'later', 'archive', 'feed'] = 'new',
        saved_using: str | None = None,
        tags: list[str] = [],
    ) -> requests.Response:
        '''
        Create a document in Readwise Reader.

        Args:
            url: Document URL
            html: Document HTML
            should_clean_html: Whether to clean the HTML
            title: Document title
            author: Document author
            summary: Document summary
            published_at: Date and time the document was published
            image_url: An image URL to use as cover image
            location: Document location
            saved_using: How the document was saved
            tags: List of tags

        Returns:
            requests.Response
        '''
        data: dict[str, Any] = {
            'url': url,
            'tags': tags,
            'location': location,
        }

        if html:
            data['html'] = html

        if should_clean_html is not None:
            data['should_clean_html'] = should_clean_html

        if title:
            data['title'] = title

        if author:
            data['author'] = author

        if summary:
            data['summary'] = summary

        if published_at:
            data['published_at'] = published_at.isoformat()

        if image_url:
            data['image_url'] = image_url

        if saved_using:
            data['saved_using'] = saved_using

        return self.post('/save/', data)
