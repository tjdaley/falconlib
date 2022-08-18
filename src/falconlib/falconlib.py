"""
falconlib.py - Client side library for Falcon API
"""
import json
import requests


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
    
    def authorize(self, username: str, password: str) -> bool:
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
            return True
        return False

    def create_tracker(self, tracker: dict) -> dict:
        """
        CreateTracker - Create a tracker

        Args:
            tracker (dict): Tracker to create
        
        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__post('/trackers', tracker)
        self.last_response = r
        return r.json()
    
    def get_tracker(self, tracker_id: str):
        """
        GetTracker - Get a tracker
        """
        r = self.__get('/trackers?tracker_id=' + tracker_id)
        self.last_response = r
        return r.json()
    
    def get_trackers(self, username: str = None) -> list:
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
        return r.json()
    
    def update_tracker(self, tracker: dict) -> dict:
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
        return r.json()
    
    def delete_tracker(self, tracker_id: str) -> dict:
        """
        DeleteTracker - Delete a tracker

        Args:
            tracker_id (str): Tracker to delete

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__delete(f'/trackers/?tracker_id={tracker_id}')
        self.last_response = r
        return r.json()
    
    def add_document(self, document: dict) -> dict:
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
        return r.json()

    def get_document(self, document_id: str) -> dict:
        """
        GetDocument - Get a document

        Args:
            document_id (str): Document to get
        
        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__get('/documents?doc_id=' + document_id)
        self.last_response = r
        print(json.dumps(r.json(), indent=4))
        return r.json()
        return r.json()
    
    def get_documents(self, tracker_id: str) -> list:
        """
        GetDocuments - Get all documents for a tracker.

        Args:
            tracker_id (str): Tracker to get documents for
        
        Returns:
            (list): List of documents.
        """
        r = self.__get(f'/trackers/{tracker_id}/documents')
        self.last_response = r
        return r.json()
    
    def update_document(self, document: dict) -> dict:
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
        return r.json()
    
    def delete_document(self, document_id: str, casecade: bool = True) -> dict:
        """
        DeleteDocument - Delete a document
    
        Args:
            document_id (str): Document to delete
        
        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__delete(f'/documents/?doc_id={document_id}&cascade={casecade}')
        self.last_response = r
        return r.json()

    def link_document(self, tracker_id: str, document_id: str) -> dict:
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
        return r.json()
    
    def unlink_document(self, tracker_id: str, document_id: str) -> dict:
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
        return r.json()

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
