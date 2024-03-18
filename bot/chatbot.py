import pymongo
import yaml
import os
import random
from Levenshtein import distance
from fuzzywuzzy import fuzz
from bson import ObjectId

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["chatbot_db"]

def load_triggers(language):
    collection = db[f"triggers_{language}"]

    # Load triggers from YAML file based on language
    yaml_file = f"bot/triggers/{language}.yaml"
    with open(yaml_file, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
        triggers = data["triggers"]
        for trigger, responses in triggers.items():
            db_trigger = {
                "trigger": trigger.lower(),
                "response": responses
            }
            # Update existing trigger or insert new trigger
            collection.update_one({"trigger": trigger.lower()}, {"$set": db_trigger}, upsert=True)

    print(f"Triggers loaded for {language.capitalize()}")


def get_response(user_input, language):
    collection = db[f"triggers_{language}"]
    
    # Check if user input matches any trigger in the database
    trigger = collection.find_one({"trigger": user_input.lower()})
    if trigger:
        return trigger["response"][0]  # Get the first response

    # Check if similar trigger already exists using Levenshtein with a threshold of 1
    similar_triggers = collection.find()
    for similar_trigger in similar_triggers:
        if distance(user_input.lower(), similar_trigger["trigger"]) <= 1:
            return similar_trigger["response"][0]  # Get the first response

    # Check if similar trigger already exists using fuzzywuzzy with a threshold of 85
    similar_triggers = collection.find()
    for similar_trigger in similar_triggers:
        if fuzz.ratio(user_input.lower(), similar_trigger["trigger"]) >= 85:
            return similar_trigger["response"][0]  # Get the first response

    # Load language-specific unknown response
    unknown_response = get_unknown_response(language)
    return unknown_response


def learn_new_trigger(user_input, language):
    collection = db[f"triggers_{language}"]
    new_trigger = {
        "trigger": user_input.lower(),
        "response": []
    }

    # Ask for the response first
    new_trigger["response"].append(input("Sure, what should I respond with when you say that? "))

    # Check if exact trigger already exists
    existing_trigger = collection.find_one({"trigger": user_input.lower()})
    if existing_trigger:
        print("A similar trigger already exists:", existing_trigger["trigger"])
        response_update = input("Would you like to update the response for this trigger? (yes/no): ")
        if response_update.lower() == "yes":
            new_trigger["response"] = existing_trigger["response"] + new_trigger["response"]
            collection.update_one({"_id": existing_trigger["_id"]}, {"$set": {"response": new_trigger["response"]}})
            print("Response updated for trigger:", existing_trigger["trigger"])
        return

    # Check if similar trigger already exists using Levenshtein with a threshold of 1
    similar_triggers = collection.find()
    for similar_trigger in similar_triggers:
        if distance(user_input.lower(), similar_trigger["trigger"]) <= 1:
            print("A similar trigger already exists:", similar_trigger["trigger"])
            response_update = input("Would you like to update the response for this trigger? (yes/no): ")
            if response_update.lower() == "yes":
                new_trigger["response"] = similar_trigger["response"] + new_trigger["response"]
                collection.update_one({"_id": similar_trigger["_id"]}, {"$set": {"response": new_trigger["response"]}})
                print("Response updated for trigger:", similar_trigger["trigger"])
            return

    # Check if similar trigger already exists using fuzzywuzzy with a threshold of 85
    similar_triggers = collection.find()
    for similar_trigger in similar_triggers:
        if fuzz.ratio(user_input.lower(), similar_trigger["trigger"]) >= 85:
            print("A similar trigger already exists:", similar_trigger["trigger"])
            response_update = input("Would you like to update the response for this trigger? (yes/no): ")
            if response_update.lower() == "yes":
                new_trigger["response"] = similar_trigger["response"] + new_trigger["response"]
                collection.update_one({"_id": similar_trigger["_id"]}, {"$set": {"response": new_trigger["response"]}})
                print("Response updated for trigger:", similar_trigger["trigger"])
            return

    collection.insert_one(new_trigger)
    print("Thanks! I'll remember that.")

    # Save learned triggers when adding new trigger
    save_learned_trigger(new_trigger, language)

def save_learned_trigger(trigger, language):
    learned_yaml_path = f"bot/learned_{language}.yaml"

    if os.path.exists(learned_yaml_path):
        with open(learned_yaml_path, "r", encoding="utf-8") as file:
            try:
                existing_triggers = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                print(exc)
                existing_triggers = None

            if existing_triggers is None or "triggers" not in existing_triggers:
                existing_trigger_list = []
            else:
                existing_trigger_list = existing_triggers["triggers"]

            trigger_dict = {
                "trigger": trigger["trigger"],
                "response": trigger["response"]
            }

            if trigger_dict not in existing_trigger_list:
                existing_trigger_list.append(trigger_dict)

            learned_triggers = {"triggers": existing_trigger_list}
    else:
        learned_triggers = {"triggers": [trigger]}

    with open(learned_yaml_path, "w", encoding="utf-8") as file:
        # Convert ObjectId to strings before dumping to YAML
        for trigger in learned_triggers["triggers"]:
            if "_id" in trigger:
                trigger["_id"] = str(trigger["_id"])
        yaml.dump(learned_triggers, file, allow_unicode=True)
    print(f"Learned trigger saved to {learned_yaml_path}")

def get_unknown_response(language):
    # Load language-specific unknown response
    translations_file = f"translations/{language}.yaml"
    with open(translations_file, "r", encoding="utf-8") as file:
        translations = yaml.safe_load(file)
        return translations["unknown"]

def main():
    print("Welcome to the ChatBot!")
    # Choose language
    while True:
        language = input("Please choose a language (estonian/english/lithuanian): ").lower()
        if language in ["estonian", "english", "lithuanian"]:
            load_triggers(language)
            print(f"Language set to {language.capitalize()}")
            break
        else:
            print("Invalid language. Please choose estonian, english, or lithuanian.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        response = get_response(user_input, language)
        print("Bot:", response.format(name=user_input))  # Format response with user input

        if response == get_unknown_response(language):
            learn_new_trigger(user_input, language)

if __name__ == "__main__":
    main()
