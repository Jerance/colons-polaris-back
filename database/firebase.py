import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage

FIREBASE_KEY_PATH = './database/credentials.json' 

cred = credentials.Certificate(FIREBASE_KEY_PATH)
firebase_admin.initialize_app(cred)

db = firestore.client()

storage_client = storage.Client.from_service_account_json(FIREBASE_KEY_PATH)
bucket = storage_client.bucket('colons-polaris.appspot.com')
