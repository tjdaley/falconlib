"""
tests_010_lib.py - Tests for falconlib.py
"""
import requests
import pytest
import json
import falconlib

API_VERSION = '1_0'
SERVER = 'http://localhost:8000'
xSERVER = 'https://api.jdbot.us'
PREFIX = f'/api/v{API_VERSION}'

test_user = {
    'email': 'test_user@test.com',
    'username': 'test_user@test.com',
    'password': 'test_password',
    'full_name': 'Test User'
}

TRACKER_ID_123 = {'id': '123', 'username': test_user['username'], 'name': 'Test Tracker', 'documents': [], 'client_reference':'20202.1', 'bates_pattern': 'TJD\\d{4}'}
TRACKER_ID_124 = {'id': '124', 'username': test_user['username'], 'name': 'Test Tracker', 'documents': [], 'client_reference':'20202.1', 'bates_pattern': 'TJD\\d{4}'}
TRACKER_NO_ID = {'username': test_user['username'], 'name': 'Test Tracker', 'documents': [], 'bates_pattern': 'TJD\\d{4}'}
DOC_1 = {
    "id": "doc-1",
    "path":"x:\\shared\\plano\\tjd\\open\\farrar\\discovery\\our production\\2022-07-15 BOA 2304.pdf",
    "filename":"2022-07-15 BOA 2304.pdf",
    "type": "application/pdf",
    "title": "BOA 2304 2022.07.15",
    "create_date":"07/01/2022",
    "document_date": "07/15/2022",
    "beginning_bates": "TD002304",
    "ending_bates": "TD002304",
    "page_count": 1,
    "client_reference": "20202.1",
}
DOC_2 = {
    "id": "doc-2",
    "path": "x:\\shared\\plano\\tjd\\open\\farrar\\discovery\\our production\\2022-08-15 BOA 2304.pdf",
    "filename": "2022-07-15 BOA 2304.pdf",
    "type": "application/pdf",
    "title": "BOA 2304 2022.08.15",
    "create_date": "07/01/2022",
    "document_date": "08/15/2022",
    "beginning_bates": "TD002305",
    "ending_bates": "TD002309",
    "page_count": 5,
    "client_reference": "20202.1",
    "added_username": "ferdinand_the_non-Existent User",
}

FALCONLIB = falconlib.FalconLib(SERVER, API_VERSION)

# Authenticate user
@pytest.mark.slow
def test_authenticate_user():
    FALCONLIB.authorize(test_user['username'], test_user['password'])
    assert FALCONLIB.auth_token is not None

# Document Tests
def test_add_document_1():
    r = FALCONLIB.add_document(DOC_1)
    assert FALCONLIB.last_response.status_code == 201
    assert r['id'] == DOC_1['id']

def test_add_document_2():
    r = FALCONLIB.add_document(DOC_2)
    assert FALCONLIB.last_response.status_code == 201
    assert r['id'] == DOC_2['id']

def test_get_document():
    r = FALCONLIB.get_document(DOC_1['id'])
    if FALCONLIB.last_response.status_code != 200:
        print("*"*80)
        print("***", json.dumps(r, indent=4))
        print("*"*80)
    assert FALCONLIB.last_response.status_code == 200
    assert r['id'] == DOC_1['id']

def test_update_document_version_fail():
    upd = DOC_1.copy()
    upd['title'] = '**Updated Document'
    r = FALCONLIB.update_document(upd)
    assert FALCONLIB.last_response.status_code == 409
    assert r['detail'] == f"Document version conflict: {upd['id']}"

def test_update_document_version_success():
    upd = FALCONLIB.get_document(DOC_1['id'])
    upd['title'] = '**Updated Document'
    r = FALCONLIB.update_document(upd)
    assert FALCONLIB.last_response.status_code == 200
    assert r['id'] == DOC_1['id']
    doc = FALCONLIB.get_document(DOC_1['id'])
    assert doc['title'] == '**Updated Document'

# Tracker Tests
def test_create_tracker_123():
    r = FALCONLIB.create_tracker(TRACKER_ID_123)
    assert FALCONLIB.last_response.status_code == 201

def test_create_tracker_124():
    r = FALCONLIB.create_tracker(TRACKER_ID_124)
    assert FALCONLIB.last_response.status_code == 201

def test_get_tracker():
    r = FALCONLIB.get_tracker(TRACKER_ID_123['id'])
    assert FALCONLIB.last_response.status_code == 200
    assert r['id'] == TRACKER_ID_123['id']

def test_get_trackers():
    r = FALCONLIB.get_trackers()
    assert FALCONLIB.last_response.status_code == 200
    assert len(r) == 2
    assert r[0]['id'] == TRACKER_ID_123['id'] or TRACKER_ID_124['id']
    assert r[1]['id'] == TRACKER_ID_123['id'] or TRACKER_ID_124['id']

def test_update_tracker():
    upd = FALCONLIB.get_tracker(TRACKER_ID_123['id'])
    upd['name'] = '**Updated Tracker'
    r = FALCONLIB.update_tracker(upd)
    assert FALCONLIB.last_response.status_code == 200
    assert r['id'] == TRACKER_ID_123['id']
    upd = FALCONLIB.get_tracker(TRACKER_ID_123['id'])
    assert upd['name'] == '**Updated Tracker'

def test_delete_tracker_124():
    r = FALCONLIB.delete_tracker(TRACKER_ID_124['id'])
    assert FALCONLIB.last_response.status_code == 200

# Test Document Linking and Unlinking
def test_link_document_1():
    r = FALCONLIB.link_document(TRACKER_ID_123['id'], DOC_1['id'])
    assert FALCONLIB.last_response.status_code == 202
    assert r['id'] == DOC_1['id']

def test_link_document_2():
    r = FALCONLIB.link_document(TRACKER_ID_123['id'], DOC_2['id'])
    assert FALCONLIB.last_response.status_code == 202
    assert r['id'] == DOC_2['id']

def test_get_documents():
    r = FALCONLIB.get_documents(TRACKER_ID_123['id'])
    assert FALCONLIB.last_response.status_code == 200
    assert len(r) == 2
    assert r[0]['id'] == DOC_1['id'] or DOC_2['id']
    assert r[1]['id'] == DOC_2['id'] or DOC_1['id']

def test_unlink_document():
    r = FALCONLIB.unlink_document(TRACKER_ID_123['id'], DOC_1['id'])
    assert FALCONLIB.last_response.status_code == 200

def test_get_documents_after_unlink():
    r = FALCONLIB.get_documents(TRACKER_ID_123['id'])
    assert FALCONLIB.last_response.status_code == 200
    assert len(r) == 1
    assert r[0]['id'] == DOC_2['id']

# Test Document Delete (after we've tested linking and unlinking)
def test_delete_document():
    r = FALCONLIB.delete_document(DOC_1['id'])
    assert FALCONLIB.last_response.status_code == 200
