"""
falconlib.py - Client side library for Falcon API
"""
from enum import Enum
from typing import Callable, Optional
import uuid
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

class FalconDataset(Enum):
    """
    Falcon dataset
    """
    TRANSFERS = 1
    CASH_BACK_PURCHASES = 2
    DEPOSITS = 3
    CHECKS = 4
    WIRE_TRANSFERS = 5
    UNIQUE_ACCOUNTS = 6
    MISSING_STATEMENTS = 7
    MISSING_PAGES = 8
    TRACKER_LIST = 9

def _success(http_status: int, message: str, payload: dict) -> dict:
    """
    Create a success response
    """
    if not isinstance(payload, dict):
        payload = {'value': payload}
    return FalconStatus(**{'success': True, 'message': message, 'http_status': http_status, 'payload': payload})

def _error(http_status: int, message: str, payload: dict) -> dict:
    """
    Create an error response
    """
    if not isinstance(payload, dict):
        payload = {'error': payload}
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
        self.username = None
        self.password = None
        self.user_id = None
        self.twilio_factor_id = None

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
            user = r.json()
            self.auth_token = user['access_token']
            self.token_type = user['token_type']
            self.auth_header = {'Authorization': self.token_type + ' ' + self.auth_token}
            self.session.headers.update(self.auth_header)
            self.username = username
            self.password = password
            self.user_id = user['user_id']
            self.twilio_factor_id = user.get('twilio_factor_id') or ''
            self.is_admin = user.get('is_admin') or False
            return _success(r.status_code, 'Authorized', user)
        return _error(r.status_code, 'Authorization failed', self.__json_or_text(r))
    
    def reauthorize(self) -> FalconStatus:
        """
        Reauthorize - Reauthorize user to Falcon API

        Returns:
            (FalconStatus): You can inquire the last_response for more information.
        """
        return self.authorize(self.username, self.password)

    #--------------------------------------------------------------------------------
    # User Management
    #--------------------------------------------------------------------------------
    
    def get_user(self, user_id: str, site_code: str) -> FalconStatus:
        """
        Retreive a user's record.

        Args:
            user_id (str): id of user to retrieve
            site_code (str): authorization code for site

        Returns:
            FalconStatus
        """
        r = self.__get(f'/users/lookup/{user_id}/{site_code}')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'User retrieved', r.json())
        return _error(r.status_code, f'Unable to retreive user with id {user_id}', self.__json_or_text(r))

    def register_user(self, user: dict, site_code: str) -> FalconStatus:
        """
        Register a new user.

        Args:
            user (dict): A dict having the following keys:
                username: str
                email: str
                full_name: str
                password: str
                twilio_factor_id: Optional[str] = ''
                phone_number: Optional[str] = ''
            site_code (str): This site's site code to verify authorization to register users

        Returns:
            (FalconStatus): You can inquire the last_response for more information
        """
        registration = {
            'username': user.username.lower().strip(),
            'email': user.email.lower().strip(),
            'full_name': user.full_name.strip(),
            'password': user.password.strip(),
            'twilio_factor_id': user.twilio_factor_id.strip(),
            'phone_number': user.phone_number.strip(),
            'site_code': (site_code or '').strip()
        }
        r = self.__post('/users/register', registration)
        self.last_response = r
        if r.status_code == 201:
            return _success(r.status_code, 'User registered', r.json())
        return _error(r.status_code, 'User registration failed', self.__json_or_text(r))
    
    #--------------------------------------------------------------------------------
    # Client Management
    #--------------------------------------------------------------------------------
    
    def client_list(self) -> FalconStatus:
        """
        Get a list of clients

        Returns:
            FalconStatus
        """
        r = self.__get('/clients/?search_field=client_id&search_value=*')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Clients retrieved', {"clients": r.json()})
        return _error(r.status_code, 'Unable to retrieve clients', self.__json_or_text(r))
    
    def create_client(self, client: dict) -> FalconStatus:
        """
        Create a new client

        Args:
            client (dict): A dict having the following keys:
                "name": str,
                "authorized_users": List[str]
                "billing_number": str,
                "enabled": True/False
        Returns:
            FalconStatus
        """
        r = self.__post('/clients', client)
        self.last_response = r
        if r.status_code == 201:
            return _success(r.status_code, 'Client created', r.json())
        return _error(r.status_code, 'Unable to create client', self.__json_or_text(r))
    
    def update_client(self, client: dict) -> FalconStatus:
        """
        Update a client

        Args:
            client (dict): A dict having the following keys:
                "client_id": str,
                "name": str,
                "authorized_users": List[str]
                "billing_number": str,
                "enabled": True/False
        Returns:
            FalconStatus
        """
        r = self.__put('/clients', client)
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Client updated', r.json())
        return _error(r.status_code, 'Unable to update client', self.__json_or_text(r))
    
    def delete_client(self, client_id: str) -> FalconStatus:
        """
        Delete a client

        Args:
            client_id (str): ID of client to delete

        Returns:
            FalconStatus
        """
        r = self.__delete(f'/clients/{client_id}')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Client deleted', r.json())
        return _error(r.status_code, 'Unable to delete client', self.__json_or_text(r))
    
    def add_authorized_user(self, client_id: str, username: str) -> FalconStatus:
        """
        Add an authorized user to a client

        Args:
            client_id (str): ID of client
            username (str): Username of user to add

        Returns:
            FalconStatus
        """
        r = self.__put(f'/clients/{client_id}/add_authorized_user/{username}', {})
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'User added', r.json())
        return _error(r.status_code, 'Unable to add user', self.__json_or_text(r))
    
    def remove_authorized_user(self, client_id: str, username: str) -> FalconStatus:
        """
        Remove an authorized user from a client

        Args:
            client_id (str): ID of client
            username (str): Username of user to remove

        Returns:
            FalconStatus
        """
        r = self.__put(f'/clients/{client_id}/remove_authorized_user/{username}', {})
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'User removed', r.json())
        return _error(r.status_code, 'Unable to remove user', self.__json_or_text(r))

    #--------------------------------------------------------------------------------
    # Tracker Management
    #--------------------------------------------------------------------------------
    
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
        return _error(r.status_code, 'Tracker creation failed', self.__json_or_text(r))

    def get_tracker(self, tracker_id: str) -> FalconStatus:
        """
        GetTracker - Get a tracker
        """
        r = self.__get('/trackers?tracker_id=' + tracker_id)
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Tracker retrieved', r.json())
        return _error(r.status_code, 'Tracker retrieval failed', self.__json_or_text(r))
    
    def get_client_trackers(self, client_id: str) -> FalconStatus:
        """
        GetClientTrackers - Get all trackers for a client

        Args:
            client_id (str): ID of client

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__get(f'/trackers/client?client_id={client_id}')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Trackers retrieved', {"trackers": r.json()})
        return _error(r.status_code, 'Trackers retrieval failed', self.__json_or_text(r))

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
        else:
            r = self.__get('/trackers/user')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Trackers retrieved', {'trackers': r.json()})
        return _error(r.status_code, 'Trackers retrieval failed', self.__json_or_text(r))

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
        r = self.__put('/trackers/', tracker)
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Tracker updated', r.json())
        return _error(r.status_code, 'Tracker update failed', self.__json_or_text(r))

    def delete_tracker(self, tracker_id: str) -> FalconStatus:
        """
        DeleteTracker - Delete a tracker

        Args:
            tracker_id (str): Tracker to delete

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__delete(f'/trackers?tracker_id={tracker_id}')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Tracker deleted', r.json())
        return _error(r.status_code, 'Tracker deletion failed', self.__json_or_text(r))

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
        r = self.__post('/documents', document)
        self.last_response = r
        if r.status_code == 201:
            return _success(r.status_code, 'Document added', r.json())
        return _error(r.status_code, 'Document addition failed', self.__json_or_text(r))

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
        return _error(r.status_code, 'Extended document properties addition failed', self.__json_or_text(r))

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
            r = self.__get('/documents/?doc_id=' + document_id)
        else:
            r = self.__get('/documents/?path=' + path)

        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Document retrieved', r.json())
        return _error(r.status_code, 'Document retrieval failed', self.__json_or_text(r))

    def get_extended_document_properties(self, document_id: str) -> FalconStatus:
        """
        GetExtendedDocumentProperties - Get extended document properties

        Args:
            document_id (str): Document to get extended properties for.

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__get('/documents/props?doc_id=' + document_id)
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Extended document properties retrieved', r.json())
        return _error(r.status_code, 'Extended document properties retrieval failed', self.__json_or_text(r))

    def get_csv_tables(self, document_id: str) -> FalconStatus:
        """
        GetCsvTables - Get CSV tables from a document

        Args:
            document_id (str): Document to get CSV tables from

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__get('/documents/tables/csv?doc_id=' + document_id)
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'CSV tables retrieved', r.json())
        return _error(r.status_code, 'CSV tables retrieval failed', self.__json_or_text(r))

    def get_json_tables(self, document_id: str) -> FalconStatus:
        """
        GetJsonTables - Get JSON tables from a document

        Args:
            document_id (str): Document to get JSON tables from

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__get('/documents/tables/json?doc_id=' + document_id)
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'JSON tables retrieved', r.json())
        return _error(r.status_code, 'JSON tables retrieval failed', self.__json_or_text(r))
    
    def get_compliance_matrix(self, tracker_id: str, classification: str) -> FalconStatus:
        """
        GetComplianceMatrix - Get compliance matrix for a tracker

        Args:
            tracker_id (str): Tracker to get compliance matrix for
            classification (str): Classification to get compliance matrix for

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__get(f'/trackers/{tracker_id}/compliance_matrix/{classification}')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Compliance matrix retrieved', r.json())
        return _error(r.status_code, 'Compliance matrix retrieval failed', self.__json_or_text(r))
    
    def get_dataset(self, tracker_id: str, dataset: FalconDataset) -> FalconStatus:
        """
        GetDataset - Get a dataset from a tracker

        Args:
            tracker_id (str): Tracker to get dataset from
            dataset (FalconDataset): Dataset to get

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__get(f'/trackers/{tracker_id}/datasets/{dataset}')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Dataset retrieved', r.json())
        return _error(r.status_code, 'Dataset retrieval failed', self.__json_or_text(r))

    def get_tracker_categories(self, tracker_id: str) -> FalconStatus:
        """
        GetTrackerCategories - Get categories for a tracker

        Args:
            tracker_id (str): Tracker to get categories for

        Returns:
            (list): List of categories
        """
        r = self.__get(f'/trackers/{tracker_id}/categories')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Categories retrieved', {'categories': r.json()})
        return _error(r.status_code, 'Categories retrieval failed', self.__json_or_text(r))

    def get_tracker_category_subcategory_pairs(self, tracker_id: str) -> FalconStatus:
        """
        GetTrackerCategorySubcategoryPairs - Get category/subcategory pairs for a tracker

        Args:
            tracker_id (str): Tracker to get category/subcategory pairs for

        Returns:
            (list): List of category/subcategory pairs
        """
        r = self.__get(f'/trackers/{tracker_id}/category_subcategory_pairs')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Category/subcategory pairs retrieved', {'category_subcategory_pairs': r.json()})
        return _error(r.status_code, 'Category/subcategory pairs retrieval failed', self.__json_or_text(r))

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
        return _error(r.status_code, 'Documents retrieval failed', self.__json_or_text(r))

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
        r = self.__put('/documents/', document)
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Document updated', r.json())
        print("@@@@ FALCONLIB @@@@", r)
        return _error(r.status_code, 'Document update failed', self.__json_or_text(r))

    def update_extended_document_properties(self, properties: dict) -> FalconStatus:
        """
        UpdateExtendedDocumentProperties - Update extended document properties

        Args:
            properties (dict): Extended document properties to update

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__put('/documents/props/', properties)
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Extended document properties updated', r.json())
        return _error(r.status_code, 'Extended document properties update failed', self.__json_or_text(r))

    def delete_document(self, document_id: str, casecade: bool = True) -> FalconStatus:
        """
        DeleteDocument - Delete a document

        Args:
            document_id (str): Document to delete

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__delete(f'/documents?doc_id={document_id}&cascade={casecade}')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Document deleted', r.json())
        return _error(r.status_code, 'Document deletion failed', self.__json_or_text(r))

    def delete_extended_document_properties(self, document_id: str) -> FalconStatus:
        """
        DeleteExtendedDocumentProperties - Delete extended document properties

        Args:
            document_id (str): Document to delete extended properties for.

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__delete(f'/documents/props?doc_id={document_id}')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Extended document properties deleted', r.json())
        return _error(r.status_code, 'Extended document properties deletion failed', self.__json_or_text(r))

    def delete_table(self, document_id: str, table_id: str) -> FalconStatus:
        """
        DeleteTable - Delete a table from a document

        Args:
            document_id (str): Document to delete table from
            table_id (str): Table to delete

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.

        Falcon API end point sample:
            documents/tables?doc_id=8b85f87afec74bcbad03400da4f33e58&table_id=a83375db-6af6-4f21-859e-96963c6a06c6
        """
        r = self.__delete(f'/documents/tables?doc_id={document_id}&table_id={table_id}')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Table deleted', r.json())
        return _error(r.status_code, 'Table deletion failed', self.__json_or_text(r))

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
        return _error(r.status_code, 'Document linking failed', self.__json_or_text(r))

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
        return _error(r.status_code, 'Document unlinking failed', self.__json_or_text(r))
    
    def enqueue(self, task: str, payload: dict, ttl: int = 4) -> FalconStatus:
        """
        Enqueue - Enqueue a task

        Args:
            task (str): Task to enqueue
            payload (dict): Payload to enqueue
            ttl (int): Time to live

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        request_id = str(uuid.uuid4())
        work_request = {
            'task': task,
            'payload': payload,
            'ttl': ttl,
            'username': self.username if self.username else 'anonymous',
            'request_id': request_id
        }
        r = self.__post(f'/util/enqueue', work_request)
        self.last_response = r
        if r.status_code == 201:
            return _success(r.status_code, f'Task enqueued: {request_id}', r.json())
        return _error(r.status_code, 'Task enqueue failed', self.__json_or_text(r))
    
    def job_status(self, request_id: str) -> FalconStatus:
        """
        JobStatus - Get job status

        Args:
            request_id (str): Request ID

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__get(f'/util/status?request_id={request_id}')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Job status retrieved', r.json())
        return _error(r.status_code, 'Job status retrieval failed', self.__json_or_text(r))
    
    def get_clients(self) -> FalconStatus:
        """
        GetClients - Get all clients

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        return self.get_client('*')
    
    def get_client(self, client_id: str) -> FalconStatus:
        """
        GetClient - Get a client

        Args:
            client_id (str): Client ID, '*' means get all clients.

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__get(f'/clients/?id={client_id}')
        self.last_response = r
        if r.status_code == 200:
            payload = r.json()
            if isinstance(payload, list):
                payload = {'clients': payload}
            return _success(r.status_code, 'Client retrieved', payload)
        return _error(r.status_code, 'Client retrieval failed', self.__json_or_text(r))
    
    def create_client(self, client: dict) -> FalconStatus:
        """
        CreateClient - Create a client

        Args:
            client (dict): Client to create

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__post('/clients', client)
        self.last_response = r
        if r.status_code == 201:
            return _success(r.status_code, 'Client created', r.json())
        return _error(r.status_code, 'Client creation failed', self.__json_or_text(r))
    
    def update_client(self, client: dict) -> FalconStatus:
        """
        UpdateClient - Update a client

        Args:
            client (dict): Client to update

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__put('/clients', client)
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Client updated', r.json())
        return _error(r.status_code, 'Client update failed', self.__json_or_text(r))
    
    def delete_client(self, client_id: str) -> FalconStatus:
        """
        DeleteClient - Delete a client

        Args:
            client_id (str): Client ID

        Returns:
            (dict): Response from server. You can inquire the last_response for more information.
        """
        r = self.__delete(f'/clients/{client_id}')
        self.last_response = r
        if r.status_code == 200:
            return _success(r.status_code, 'Client deleted', r.json())
        return _error(r.status_code, 'Client deletion failed', self.__json_or_text(r))

    def __json_or_text(self, result):
        """
        Return result.json() if possible, otherwise result.text()

        Args:
            result (requests.result): Result to be examined

        Returns:
            Either json or text, depending on which one we have.
        """
        try:
            return result.json()
        except ValueError:
            return result.text
    
    def __httpop(self, method: Callable, **kwargs) -> requests.Response:
        """
        HTTP Operation - Perform an HTTP operation

        Args:
            method (function): HTTP Requests method
            **kwargs: Keyword arguments
            url (str): URL (alwasys required)
            json (dict): JSON data (optional)
            data (any): Data (optional)

        Returns:
            (requests.Response): Response from server
        """
        response = method(**kwargs)
        self.last_response = response
        if response.status_code == 401:
            self.reauthorize()
            response = method(**kwargs)
            self.last_response = response
        return response

    def __get(self, url: str):
        """
        Get - Get data from Falcon API
        """
        return self.__httpop(self.session.get, url=self.base_url + url)

    def __post(self, url:str, data: dict):
        """
        Post - Post data to Falcon API
        """
        return self.__httpop(self.session.post, url=self.base_url + url, json=data)

    def __put(self, url: str, data: dict):
        """
        Put - Put data to Falcon API
        """
        return self.__httpop(self.session.put, url=self.base_url + url, json=data)

    def __delete(self, url: str):
        """
        Delete - Delete data from Falcon API
        """
        return self.__httpop(self.session.delete, url=self.base_url + url)

    def __patch(self, url: str, data=None):
        """
        Patch - Patch data to Falcon API
        """
        return self.__httpop(self.session.patch, url=self.base_url + url, data=data)

    def __options(self, url: str):
        """
        Options - Get options from Falcon API
        """
        return self.__httpop(self.session.options, url=self.base_url + url)

    def __head(self, url: str):
        """
        Head - Get head from Falcon API
        """
        return self.__httpop(self.session.head, url=self.base_url + url)

    def __trace(self, url):
        """
        Trace - Get trace from Falcon API
        """
        return self.__httpop(self.session.trace, url=self.base_url + url)

    def __connect(self, url: str):
        """
        Connect - Get connect from Falcon API
        """
        return self.__httpop(self.session.connect, url=self.base_url + url)

    def options(self, url):
        """
        Options - Get options from Falcon API
        """
        return self.__httpop(self.session.options, url=self.base_url + url)
