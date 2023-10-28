import json
import requests
import sys
import yaml

def invoke(action, params={}):
    request = {'action': action, 'params': params, 'version': 6}
    response = requests.post('http://localhost:8765', json=request).json()

    if len(response) != 2:
        raise Exception("response has an unexpected number of fields")
    if 'error' not in response:
        raise Exception("response is missing required error field")
    if 'result' not in response:
        raise Exception("response is missing required result field")
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']

def import_cards_into_anki_deck(data, config):
    anki_deck_name = config['anki_deck_name']
    field_mapping = config['field_mapping']

    for deck in data['~:decks']:
        cards_data = deck['~:cards']['~#list']
        for card_data in cards_data:
            fields = {}
            for mochi_field, anki_field in field_mapping.items():
                try:
                    fields[anki_field] = card_data['~:fields'][mochi_field]['~:value']
                except KeyError:
                    print(f"Field {mochi_field} not found in card {card_data['~:id']}")
                    fields[anki_field] = ""

            anki_note = {
                "deckName": anki_deck_name,
                "modelName": config['anki_model_name'],
                "fields": fields,
                "tags": [],
            }

            try:
                result = invoke('addNote', {'note': anki_note})
            except Exception as e:
                print(f"Error adding card {card_data['~:id']}: {e}")
                continue            

if __name__ == '__main__':
    # Load the configuration from the YAML file
    config_filepath = None
    data_filepath = None

    for arg in sys.argv:
        if arg.endswith('.yml'):
            config_filepath = arg
        elif arg.endswith('.json'):
            data_filepath = arg
        
    if config_filepath is None or data_filepath is None:
        print("Usage: python import_anki_cards.py config.yml data.json")
        sys.exit(1)

    with open(config_filepath, 'r') as config_file:
        print("Loading config...")
        config = yaml.safe_load(config_file)
    
    # Load the data from the JSON file
    with open(data_filepath, 'r') as data_file:
        print("Loading data...")
        data = json.load(data_file)

    print("Importing cards into Anki deck...")
    import_cards_into_anki_deck(data, config)
    print("Done!")
