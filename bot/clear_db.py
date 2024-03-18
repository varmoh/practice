import pymongo

def clear_database():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["chatbot_db"]
    
    # List all collections in the database
    collections = db.list_collection_names()

    for collection_name in collections:
        db[collection_name].drop()
        print(f"Collection '{collection_name}' dropped.")

    print("All collections have been dropped.")

if __name__ == "__main__":
    clear_database()
