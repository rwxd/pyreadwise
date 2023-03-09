# Advanced Usage

## Custom request

You can use the `get`, `post`, `delete` or `request` methods to make a custom request.

```python
from readwise import Readwise

client = Readwise('token')
response = client.get('/books/', params={'category': 'articles'})
response.raise_for_status()
print(response.json())
```

Custom http method

```python
from readwise import Readwise

client = Readwise('token')
response = client.request('get', '/books/', params={'category': 'articles'})
response.raise_for_status()
print(response.json())
```

## Pagination

A helper method for pagination is available.

```python
from readwise import Readwise

client = Readwise('token')
for response in client.get_pagination('/books/', params={'category': 'articles'}):
	response.raise_for_status()
	for book in response.json()['results']:
		print(book)
```
