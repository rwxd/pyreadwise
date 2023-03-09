# Python Module to use the Readwise API

This module is a wrapper for the Readwise API.

It allows you to easily access your Readwise data in Python.

## Installation

```bash
pip install -U readwise
```

## How to use

### Readwise API

```python
from readwise import Readwise

client = Readwise('token')

books = client.get_books(category='articles')

for book in books:
	highlights = client.get_book_highlights(book.id)
	if len(highlights) > 0:
		print(book.title)
		for highlight in highlights:
			print(highlight.text)
```

### Readwise Readwise API

```python
from readwise import ReadwiseReader

client = ReadwiseReader('token')

response = client.create_document('https://www.example.com')
response.raise_for_status()
```

## Documentation

The latest documentation can be found at <https://rwxd.github.io/pyreadwise/>

If you've checked out the source code (for example to review a PR), you can build the latest documentation by running `make serve-docs`.
