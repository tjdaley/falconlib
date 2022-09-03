"""
falconlib.py - Client side library for Falcon API
"""
import json
import requests
from pydantic import BaseModel

class FalconStatus(BaseModel):
    """
    Falcon status
    """
    success: bool
    message: str
    http_status: int
    payload: dict

def _success(http_status: int, message: str, payload: dict) -> dict:
    """
    Create a success response
    """
    return FalconStatus(**{'success': True, 'message': message, 'http_status': http_status, 'payload': payload})

def _error(http_status: int, message: str, payload: dict) -> dict:
    """
    Create an error response
    """
    return FalconStatus(**{'success': False, 'message': message, 'http_status': http_status, 'payload': payload})

class FalconLib:
    """
    FalconLib - Client side library for Falcon API
    """
    def __init__(self, base_url: str, version: str = '1_0') -> None:
        """
        FalconLib - Client side library for Falcon API

        Args:
            base_url (str): Base URL of Falcon API
            version (str): Version of Falcon API
        
        Returns:
            None
        """
        self.base_url = base_url + '/api/v' + version
        self.version = version
        self.auth_token = None
        self.token_type = None
        self.auth_header = None
        self.username = None
        self.session = requests.Session()
        self.last_response = None
    
    def authorize(self, username: str, password: str) -> FalconStatus:
        """
        Authorize - Authorize user to Falcon API

        Args:
            username (str): Username of user
            password (str): Password of user
        
        Returns:
            (bool): True if authorized, False if not. You can inquire the last_response for more information.
        """
        r = requests.post(self.base_url + '/users/token', data={'username': username, 'password': password})
        self.last_response = r
        if r.status_code == 200:
            self.auth_token = r.json()['access_token']
            self.token_type = r.json()['token_type']
            self.auth_header = {'Authorization': self.token_type + ' ' + self.auth_token}
            self.session.headers.update(self.auth_header)
            self.username = username
            return _success(r.status_code, 'Authorized', r.json())
        return _error(r.status_code, 'Authorization failed', r.json())

    def create_tracker(self, tracker: dict) -> FalconStatus:
        """
        CreateTracker - Create a tracker

        Args:
            tracker (dict): Tracker to create
        
        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__post('/trackers', tracker)
        self.last_response = r
        if r.status_code == 201:
            return _success(r.status_code, 'Tracker created', r.json())
        return _error(r.status_code, 'Tracker creation failed', r.json())
    
    def get_tracker(self, tracker_id: str) -> FalconStatus:
        """
        GetTracker - Get a tracker
        """
        r = self.__get('/trackers?tracker_id=' + tracker_id)
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Tracker retrieved', r.json())
        return _error(r.status_code, 'Tracker retrieval failed', r.json())
    
    def get_trackers(self, username: str = None) -> FalconStatus:
        """
        GetTrackers - Get all trackers for a user. If no username is provided,
        all trackers for the authenticated user are returned. Your account must
        have the 'admin' role to specify a username other than the authenticated user.

        Args:
            username (str): Username of user
        
        Returns:
            (list): List of trackers
        """
        if username:
            r = self.__get('/trackers/user?username=' + username)
        r = self.__get('/trackers/user')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Trackers retrieved', {'trackers': r.json()})
        return _error(r.status_code, 'Trackers retrieval failed', r.json())
    
    def update_tracker(self, tracker: dict) -> FalconStatus:
        """
        UpdateTracker - Update a tracker.
        
        You cannot update the username or
        documents list. *All* fields in the tracker are updated. If you
        omit a field, the field will be set to None on the server. The best
        practice is to retrieve the current trcker, update fields that you want
        to change, and submit the updated tracker.
    
        Args:
            tracker (dict): Tracker to update
        
        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        tracker.pop('documents', None)
        r = self.__put(f'/trackers/', tracker)
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Tracker updated', r.json())
        return _error(r.status_code, 'Tracker update failed', r.json())
    
    def delete_tracker(self, tracker_id: str) -> FalconStatus:
        """
        DeleteTracker - Delete a tracker

        Args:
            tracker_id (str): Tracker to delete

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__delete(f'/trackers/?tracker_id={tracker_id}')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Tracker deleted', r.json())
        return _error(r.status_code, 'Tracker deletion failed', r.json())
    
    def add_document(self, document: dict) -> FalconStatus:
        """
        AddDocument - Add a document to the database

        This method does not add a document to a tracker. To add a document to a tracker,
        use the link_document and unlink_document methods.

        Args:
            document (dict): Document to add
        
        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__post(f'/documents', document)
        self.last_response = r
        if r.status_code == 201:
            return _success(r.status_code, 'Document added', r.json())
        return _error(r.status_code, 'Document addition failed', r.json())

    def add_extended_document_properties(self, properties: dict) -> FalconStatus:
        """
        AddExtendedDocumentProperties - Add extended document properties

        Args:
            properties (dict): Extended document properties to add
        
        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__post(f'/documents/props', properties)
        self.last_response = r
        if r.status_code == 201:
            return _success(r.status_code, 'Extended document properties added', r.json())
        return _error(r.status_code, 'Extended document properties addition failed', r.json())

    def get_document(self, document_id: str = None, path: str = None) -> FalconStatus:
        """
        Get a document from the database.
        You can specify either the document_id or the path. If you specify both,
        the document_id takes precedence. You must specify one of the two.

        Args:
            document_id (str): Document to get (Optional)
            path (str): Path to document to get (Optional)
        
        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        if not document_id and not path:
            raise ValueError('You must specify either the document_id or the path')
        
        if document_id:
            r = self.__get('/documents?doc_id=' + document_id)
        else:
            r = self.__get('/documents?path=' + path)

        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Document retrieved', r.json())
        return _error(r.status_code, 'Document retrieval failed', r.json())
    
    def get_extended_document_properties(self, document_id: str) -> FalconStatus:
        """
        GetExtendedDocumentProperties - Get extended document properties

        Args:
            document_id (str): Document to get extended properties for.

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__get('/documents/props/?doc_id=' + document_id)
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Extended document properties retrieved', r.json())
        return _error(r.status_code, 'Extended document properties retrieval failed', r.json())
    
    def get_documents(self, tracker_id: str) -> FalconStatus:
        """
        GetDocuments - Get all documents for a tracker.

        Args:
            tracker_id (str): Tracker to get documents for
        
        Returns:
            (list): List of documents.
        """
        r = self.__get(f'/trackers/{tracker_id}/documents')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Documents retrieved', {'documents': r.json()})
        return _error(r.status_code, 'Documents retrieval failed', r.json())
    
    def update_document(self, document: dict) -> FalconStatus:
        """
        UpdateDocument - Update a document

        *ALL* fields in the document are updated. The best practice is to
        retrieve the current document, update fields that you want to change,
        and submit the updated document.

        Args:
            document (dict): Document to update
        
        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__put(f'/documents/', document)
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Document updated', r.json())
        return _error(r.status_code, 'Document update failed', r.json())
    
    def update_extended_document_properties(self, properties: dict) -> FalconStatus:
        """
        UpdateExtendedDocumentProperties - Update extended document properties

        Args:
            properties (dict): Extended document properties to update
        
        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__put(f'/documents/props/', properties)
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Extended document properties updated', r.json())
        return _error(r.status_code, 'Extended document properties update failed', r.json())
    
    def delete_document(self, document_id: str, casecade: bool = True) -> FalconStatus:
        """
        DeleteDocument - Delete a document
    
        Args:
            document_id (str): Document to delete
        
        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__delete(f'/documents/?doc_id={document_id}&cascade={casecade}')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Document deleted', r.json())
        return _error(r.status_code, 'Document deletion failed', r.json())
    
    def delete_extended_document_properties(self, document_id: str) -> FalconStatus:
        """
        DeleteExtendedDocumentProperties - Delete extended document properties

        Args:
            document_id (str): Document to delete extended properties for.
        
        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__delete(f'/documents/props/?doc_id={document_id}')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Extended document properties deleted', r.json())
        return _error(r.status_code, 'Extended document properties deletion failed', r.json())

    def link_document(self, tracker_id: str, document_id: str) -> FalconStatus:
        """
        LinkDocument - Link a document to a tracker

        Args:
            tracker_id (str): Tracker to link document to
            document_id (str): Document to link to tracker
        
        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__patch(f'/trackers/{tracker_id}/documents/link/{document_id}')
        self.last_response = r
        if r.status_code == 202:
            return _success(r.status_code, 'Document linked', r.json())
        return _error(r.status_code, 'Document linking failed', r.json())
    
    def unlink_document(self, tracker_id: str, document_id: str) -> FalconStatus:
        """
        UnlinkDocument - Unlink a document from a tracker

        Args:
            tracker_id (str): Tracker to unlink document from
            document_id (str): Document to unlink from tracker
        
        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__patch(f'/trackers/{tracker_id}/documents/unlink/{document_id}')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Document unlinked', r.json())
        return _error(r.status_code, 'Document unlinking failed', r.json())

    def __get(self, url: str):
        """
        Get - Get data from Falcon API
        """
        return self.session.get(self.base_url + url)

    def __post(self, url:str, data: dict):
        """
        Post - Post data to Falcon API
        """
        return self.session.post(self.base_url + url, json=data)

    def __put(self, url: str, data: dict):
        """
        Put - Put data to Falcon API
        """
        return self.session.put(self.base_url + url, json=data)

    def __delete(self, url: str):
        """
        Delete - Delete data from Falcon API
        """
        return self.session.delete(self.base_url + url)

    def __patch(self, url: str, data=None):
        """
        Patch - Patch data to Falcon API
        """
        return self.session.patch(self.base_url + url, data=data)

    def __options(self, url: str):
        """
        Options - Get options from Falcon API
        """
        return self.session.options(self.base_url + url)

    def __head(self, url: str):
        """
        Head - Get head from Falcon API
        """
        return self.session.head(self.base_url + url)

    def __trace(self, url):
        """
        Trace - Get trace from Falcon API
        """
        return self.session.trace(self.base_url + url)

    def __connect(self, url: str):
        """
        Connect - Get connect from Falcon API
        """
        return self.session.connect(self.base_url + url)

    def options(self, url):
        """
        Options - Get options from Falcon API
        """
        return self.session.options(self.base_url + url)
