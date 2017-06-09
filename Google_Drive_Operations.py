import httplib2
import os

from apiclient import discovery
from apiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from Helper_Functions import *

SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API'
CREDENTIALS_FILE_NAME = 'Credentials.json'

def get_credentials():
    try:
        import argparse
        Google_Drive_Flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        Google_Drive_Flags = None
    
    Credential_Path = CREDENTIALS_FILE_NAME
    Store = Storage(Credential_Path)
    Credentials = Store.get()
    if not Credentials or Credentials.invalid:
        Flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        Flow.user_agent = APPLICATION_NAME
        if Google_Drive_Flags:
            Credentials = tools.run_flow(Flow, Store, Google_Drive_Flags)
        else: # Needed only for compatibility with Python 2.6
            Credentials = tools.run(Flow, Store)
    return Credentials

def create_service():
    Credentials = get_credentials()
    HTTP = Credentials.authorize(httplib2.Http())
    Service = discovery.build('drive', 'v3', http=HTTP)
    return Service

def get_folder_list(Service):
    Folder_List ={}
    Response = Service.files().list(
                                    q = "mimeType = 'application/vnd.google-apps.folder'",
                                    pageSize = 10,
                                    fields = "nextPageToken, files(id, name)"
                                  ).execute()
    while True:
        Folder_Items = Response.get('files', [])
        if Folder_Items:
            for Item in Folder_Items:
                Folder_List[Item['name']] = Item['id']
        
        Next_Page_Token = Response.get('nextPageToken', None)
        if Next_Page_Token is None:
            break
        
        Response = service.files().list(
                                    pageToken = Next_Page_Token,
                                    q = "mimeType = 'application/vnd.google-apps.folder'",
                                    pageSize = 10,
                                    fields = "nextPageToken, files(id, name)"
                                  ).execute()
    
    return Folder_List
                                  
def upload_files(Service,File_Name,Folder_ID = None,File_Mime_Type = None,Google_Mime_Type = None):
    Google_File_Name = os.path.basename(File_Name).split('.')[0]
    if Google_Mime_Type:
        File_Metadata = {
                            'name' : Google_File_Name,
                            'mimeType' : Google_Mime_Type
                        }
    else:
        File_Metadata = {
                            'name' : Google_File_Name
                        }
    if Folder_ID:
        File_Metadata['parents'] = [Folder_ID]
    
    Media = MediaFileUpload(File_Name, mimetype = File_Mime_Type, resumable = True)
    
    Google_File = Service.files().create(
                                           body = File_Metadata,
                                           media_body = Media,
                                           fields = 'id'
                                        ).execute()
    
    if Google_File.get('id',None):
        return True
    else:
        return False
    
def main(CSV_File):
    Logger = logging.getLogger(LOGGER_NAME)
    Logger.info('Google Drive Operations Started')
    try:
        Service = create_service()
        if Service is None:
            raise Exception()
    except Exception as e:
        Logger.error('Exception in generating Google Drive Service', exc_info=True)
        return None
    
    Folder_List = get_folder_list(Service)
    if not Folder_List:
        Logger.error('No Folders Defined For Operation')
        return None
    
    if CSV_FOLDER not in Folder_List.keys() or LOGS_FOLDER not in Folder_List.keys():
        Logger.error('%s or %s Folder Not Present'%(CSV_FOLDER,LOGS_FOLDER))
        return None
    
    if upload_files(Service,CSV_File,Folder_ID = Folder_List.get(CSV_FOLDER,None), 
                    File_Mime_Type = 'text/csv' ,Google_Mime_Type = 'application/vnd.google-apps.spreadsheet') == True:
        Logger.info('%s File Uploaded'%(CSV_File))
    else:
        Logger.error('%s Upload Failure'%(CSV_File))
    
    Logger.info('Google Drive CSV Operations Ended')
    
    Log_Folder_ID = Folder_List.get(LOGS_FOLDER,None)
    
    return (Service,Log_Folder_ID)