import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId

load_dotenv()

mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/smartserve_db")

class FallbackCollection:
    def __init__(self, name):
        self.name = name
        self._data = []

    def find_one(self, filter=None, *args, **kwargs):
        if not filter:
            return self._data[0] if self._data else None
        for doc in self._data:
            match = True
            for k, v in filter.items():
                if k.startswith("$"):
                    continue
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                return doc
        return None

    def find(self, filter=None, *args, **kwargs):
        if not filter:
            return list(self._data)
        results = []
        for doc in self._data:
            match = True
            for k, v in filter.items():
                if k.startswith("$"):
                    continue
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                results.append(doc)
        return results

    def insert_one(self, document):
        if "_id" not in document:
            document["_id"] = ObjectId()
        self._data.append(document)
        class InsertResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        return InsertResult(document["_id"])

    def insert_many(self, documents):
        for doc in documents:
            self.insert_one(doc)

    def update_one(self, filter, update):
        doc = self.find_one(filter)
        if doc and "$set" in update:
            doc.update(update["$set"])

    def delete_one(self, filter):
        doc = self.find_one(filter)
        if doc in self._data:
            self._data.remove(doc)

    def count_documents(self, filter):
        return len(self.find(filter))

class FallbackDatabase:
    def __init__(self):
        self._collections = {}

    def __getitem__(self, name):
        if name not in self._collections:
            self._collections[name] = FallbackCollection(name)
        return self._collections[name]

def get_database():
    # 1. Try Primary configured MONGO_URI
    if mongo_uri:
        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
            client.admin.command('ping')
            print("Successfully connected to primary MongoDB URI.")
            return client["smartserve_db"]
        except Exception as e:
            print(f"Primary MongoDB URI connection failed ({type(e).__name__}: {e}). Trying local MongoDB...")

    # 2. Try Local MongoDB instance
    try:
        local_client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        local_client.admin.command('ping')
        print("Successfully connected to local MongoDB (localhost:27017).")
        return local_client["smartserve_db"]
    except Exception as local_e:
        print(f"Local MongoDB connection failed ({type(local_e).__name__}: {local_e}). Using built-in in-memory database...")

    # 3. Use Built-in In-Memory Fallback
    return FallbackDatabase()

db = get_database()

users = db["users"]
providers = db["providers"]
bookings = db["bookings"]
payments = db["payments"]
time_slots = db["time_slots"]