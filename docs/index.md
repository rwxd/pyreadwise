# Python Module to use the Readwise API

## Installation

```bash
pip install -U readwise
```

## Quickstart

### Readwise API

```python
from readwise import ReadwiseClient

client = ReadwiseClient('token')

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
from readwise import ReadwiseReaderClient

client = ReadwiseReaderClient('token')

response = client.create_document('https://www.example.com')
response.raise_for_status()
```
