import yaml
import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["chatbot_db"]

def load_triggers(language):
    # Load triggers from database
    collection = db[f"triggers_{language}"]
    triggers = list(collection.find())
    return triggers

def save_intents(triggers, language):
    intents_path = f"bot/intents/intents_{language}.yaml"
    intents = {"intents": []}

    for trigger in triggers:
        intents["intents"].append({
            "trigger": trigger["trigger"],
            "responses": [trigger["response"]]
        })

    with open(intents_path, "w", encoding="utf-8") as file:
        yaml.dump(intents, file, allow_unicode=True)
    print(f"Intents saved to {intents_path}")

def main():
    print("Generating Intents File...")
    # Choose language
    language = input("Please choose a language (estonian/english/lithuanian): ").lower()
    if language in ["estonian", "english", "lithuanian"]:
        triggers = load_triggers(language)
        save_intents(triggers, language)
        print(f"Intents file generated for {language.capitalize()}")
    else:
        print("Invalid language. Please choose estonian, english, or lithuanian.")

if __name__ == "__main__":
    main()
