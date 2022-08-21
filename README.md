# falconlib
Python client lib for accessing Falcon API

*Falconlib* is the preferred means of accessing my back-end services. With the proper credentials,
you can access some of those back-end services through the *requests* pacakge, but they change
frequently and move from endpoint to endpoint. *Falconlib* smoothes out those developmental
undulations.

# GETTING STARTED

## Installation

```pip install falconlib```

## Instantiation

```python
from falconlib import FalconlLib

falconlib = FalconLib('https://your-endpoint.com')
falconlib.authorize('my_username', 'my_password')
```

# NOTES

The *requests* package handles the HTTPS traffic between *falconlib* and the back-end services.
Because of that, you can access the last *response* object thus:

```python
r = falconlib.last_response
```

# HTTP STATUS CODES

If an API call fails, the HTTP status code will be one of these:

| Status Code | Explanation |
|----------|---------------------------------|
| 401 | Invalid login credentials |
| 404 | Object not found, e.g. Document, Tracker, etc. |
| 409 | Conflict. Check falconlib.last_response.json() for a specific explanation |
| 500 | Server-side error. Sorry about that. |

# DOCUMENT MANAGEMENT

## Add a document to the database
*add_document(doc: dict) -> dict*

*Arguments*

*doc* (dict) - Elements of a [Document](https://api.jdbot.us/docs#model-Document)

*Result*

Upon successful insert:

    (dict) - ```{"message": "Document added", "id": "doc-1"}```

 or, if *last_response.status_code* > 200, an error such as:

    (dict) - ```{"detail": "Document already exists: doc_id"}```

```python
DOC_1 = {
    "id": "doc-1",
    "path":"x:\\shared\\office\\user\\client\\discovery\\our production\\my_document.pdf",
    "filename":"my_document.pdf",
    "type": "application/pdf",
    "title": "my_document",
    "create_date":"07/01/2022",
    "document_date": "07/15/2022",
    "beginning_bates": "TD002304",
    "ending_bates": "TD002304",
    "page_count": 1,
    "client_reference": "20202.1",
}

r = FALCONLIB.add_document(DOC_1)
assert FALCONLIB.last_response.status_code == 201
```

## get_document() - Retrieve a document from the database

```python
doc = FALCONLIB.get_document(DOC_1['id'])
assert FALCONLIB.last_response.status_code == 200
assert r['id'] == DOC_1['id']
```

## update_document() - Update a document in the database

```python
# Retrieve document before updating to avoid version conflicts.
upd = FALCONLIB.get_document(DOC_1['id'])

# Update the field(s) you want to revise.
upd['title'] = '**Updated Document'

# Update the document
r = FALCONLIB.update_document(upd)

# Status codes:
# 200 = Success
# 404 = Document not found
# 401 = Authorization error
# 409 = Version conflict (retrieve and try again)
assert FALCONLIB.last_response.status_code == 200
```

## delete_document() - Delete a document from the database

### *Arguments*

*document_id*: (str) - ID of document to delete. (required)

*cascade* (bool) - Whether to cascade the delete. (optional, default=True)
If *cascade* is set to True, then the document will be deleted and removed from all trackers
that reference it. If *cascade* is set to False, then the document will be deleted only if
it is not linked to any trackers.

```python
FALCONLIB.delete_document(document_id=DOC_1['id'], cascade=False)
assert FALCONLIB.last_response.status_code == 200
```

# TRACKER MANAGEMENT
