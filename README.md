# falconlib
Python client lib for accessing Falcon API

<p align="center">
    <a href="https://github.com/tjdaley/falconlib/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/tjdaley/falconlib"></a>
    <a href="https://github.com/tjdaley/falconlib/network"><img alt="GitHub forks" src="https://img.shields.io/github/forks/tjdaley/falconlib"></a>
    <a href="https://github.com/tjdaley/falconlib/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/tjdaley/falconlib"><a>
    <img alt="Stage: Development" src="https://img.shields.io/badge/stage-Development-orange">
    <img alt="PyPI - License" src="https://img.shields.io/pypi/l/falconlib">
</p>
<p align="center">
    <a href="#purpose">Purpose</a> &bull;
    <a href="#installation">Installation</a> &bull;
    <a href="#notes">Notes</a> &bull;
    <a href="#document-management">Document Management</a> &bull;
    <a href="#author">Author</a>
</p>

## Purpose

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

# FUNCTION RETURNS

All functions return a FalconStatus object having these fields:

| Field | Type | Value |
|-------|------|-------|
| *success* | (bool)  | True if successful otherwise False |
| *status* | (int) | HTTP status of last HTTP(s) request |
| *message* | (str) | Message that explains the success or failure of the function call |
| *payload* | (dict) | Contains the payload of the function call and is documented with each method below |

# DOCUMENT MANAGEMENT

## Add a document to the database

### *add_document(doc: dict) -> FalconStatus*

***Arguments***

*doc* (dict) - Elements of a [Document](https://api.jdbot.us/docs#model-Document)

***Result***

Instance of *FalconStatus*

### Example

```python
from falconlib import FalconlLib

falconlib = FalconLib('https://your-endpoint.com')
falconlib.authorize('my_username', 'my_password')

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

fstatus = falconlib.add_document(DOC_1)
assert fstatus.success == True
assert falconlib.last_response.status_code == 201
```
## Retrieve a Document from the Database

### *get_document(document_id: str, path: str) -> FalconStatus*

***Arguments***

document_id (str): *id* of the document to be retrieved. (optional)
path (str): *path* of the document to be retrieved. (optional)

You must provide *either* a *document_id* or a *path*. If you provide both, then
*document_id* will be used. If you provide neither, the call will raise an exception.

***Result***

Instance of *FalconStatus* where the *payload* field contains a
*dict* having the elements of a [Document](https://api.jdbot.us/docs#model-Document)

### Example

```python
from falconlib import FalconlLib

falconlib = FalconLib('https://your-endpoint.com')
falconlib.authorize('my_username', 'my_password')

doc = falconlib.get_document('doc-1').payload
assert falconlib.last_response.status_code == 200
assert doc['id'] == 'doc-1'
```
## Update a Document in the Database

### *update_document(revised_doc: dict) -> FalconStatus*

***Arguments***

*revised_doc* (dict) - Elements of a [Document](https://api.jdbot.us/docs#model-Document)

***Result***

Instance of *FalconStatus*

### Example

```python
from falconlib import FalconlLib

falconlib = FalconLib('https://your-endpoint.com')
falconlib.authorize('my_username', 'my_password')

# Retrieve document before updating to avoid version conflicts.
revised_doc = falconlib.get_document(DOC_1['id']).payload

# Update the field(s) you want to revise.
revised_doc['title'] = '**Updated Document'

# Update the document
r = falconlib.update_document(revised_doc)
assert r.success == True
assert falconlib.last_response.status_code == 200
```

## Delete a Document from the Database
### *delete_document(document_id: str, cascade: bool = True) -> FalconStatus*

### *Arguments*

*document_id*: (str) - ID of document to delete. (required)

*cascade* (bool) - Whether to cascade the delete. (optional, default=True)
If *cascade* is set to True, then the document will be deleted and removed from all trackers
that reference it. If *cascade* is set to False, then the document will be deleted only if
it is not linked to any trackers.

```python
from falconlib import FalconlLib

falconlib = FalconLib('https://your-endpoint.com')
r = falconlib.authorize('my_username', 'my_password')
r = falconlib.delete_document(document_id=DOC_1['id'], cascade=False)
assert r.success == True
assert falconlib.last_response.status_code == 200
```

# TRACKER MANAGEMENT

# MAINTENANCE

Before posting a new version, run pytest and make sure all tests are passing.

Next, make sure to bump the version in falconlib.toml

Then, build a new version:

```py -m build```

Finally, upload the new version:

```py -m twine upload dist/*```

For detailed instructions, visit (https://packaging.python.org)[https://packaging.python.org/en/latest/tutorials/packaging-projects/].

# Author

Thomas J. Daley, J.D. is an active family law litigation attorney practicing primarily in Collin County, Texas and software developer. My family law practice is limited to divorce, child custody, child support, enforcment, and modification suits. [Web Site](https://koonsfuller.com/attorneys/tom-daley/)