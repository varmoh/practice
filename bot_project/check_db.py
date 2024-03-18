import pymongo

def print_database_contents():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["chatbot_db"]
    
    # List all collections in the database
    collections = db.list_collection_names()

    for collection_name in collections:
        print(f"Collection: {collection_name}")
        collection = db[collection_name]
        all_documents = collection.find()

        for document in all_documents:
            print(document)
        print("-" * 20)

if __name__ == "__main__":
    print_database_contents()
