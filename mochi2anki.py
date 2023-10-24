import json
import random
import yaml
import os
import genanki
import sys

def generate_anki_id():
    return random.randrange(1 << 30, 1 << 31)

def create_anki_deck(data, config):
    decks = data['~:decks']

    front_fields = config['front']["fields"]
    back_fields = config['back']["fields"]
    fields = front_fields + back_fields

    # Create template based on the configuration
    front_template = "<br>".join(["{{" + field['name'] + "}}" for field in front_fields])
    back_template = "<br>".join(["{{" + field['name'] + "}}" for field in back_fields])

    templates = {
        'name': config['anki_template_name'],
        'qfmt': front_template,
        'afmt': back_template,
    }

    model = genanki.Model(
        generate_anki_id(),  # Some random model ID
        config['anki_model_name'],
        fields=fields,
        templates=[templates]
    )

    # Create the Anki deck
    anki_deck = genanki.Deck(
        generate_anki_id(),  # Some random deck ID
        data['~:decks'][0]['~:name']
    )

    for deck in decks:

        cards_data = deck['~:cards']['~#list']
        deck_template_id = None
        try:
            deck_template_id = deck['~:template-id']
        except KeyError:
            print(f"Deck {deck['~:name']} has no template-id")
            
        for card_data in cards_data:
            card_template_id = deck_template_id
            try:
                card_template_id = card_data['~:template-id']
            except KeyError:
                print(f"Card {card_data['~:id']} has no template-id, using deck template-id")

            if card_template_id is None:
                print(f"Card {card_data['~:id']} has no template-id, skipping")
                continue

            if card_template_id != config['template_id']:
                print(f"Card {card_data['~:id']} has template-id {card_template_id}, skipping")
                continue

            fields_data = []

            front_fields_data = []
            back_fields_data = []

            for field in front_fields:
                try:
                    front_fields_data.append(card_data['~:fields'][field['id']]['~:value'])
                except KeyError:
                    front_fields_data.append("")
                    print(f"Field {field['id']} not found in card {card_data['~:id']}")

            for field in back_fields:
                try:
                    back_fields_data.append(card_data['~:fields'][field['id']]['~:value'])
                except KeyError:
                    back_fields_data.append("")
                    print(f"Field {field['id']} not found in card {card_data['~:id']}")

            fields_data = front_fields_data + back_fields_data

            card = genanki.Note(
                model=model,
                fields=fields_data
            )
            anki_deck.add_note(card)

    # Save the deck to a file
    genanki.Package(anki_deck).write_to_file(config.get('output_file', 'output.apkg'))

if __name__ == '__main__':
    # Load the configuration from the YAML file
    # get config file and data file from args

    config_filepath = None
    data_filepath = None

    for arg in sys.argv:
        if arg.endswith('.yml'):
            config_filepath = arg
        elif arg.endswith('.json'):
            data_filepath = arg
        
    if config_filepath is None or data_filepath is None:
        print("Usage: python convert.py config.yml data.json")
        exit(1)

    with open(config_filepath, 'r') as config_file:
        print("Loading config...")
        config = yaml.safe_load(config_file)
    
    # Load the data from the JSON file
    with open(data_filepath, 'r') as data_file:
        print("Loading data...")
        data = json.load(data_file)

    print("Creating Anki deck...")
    create_anki_deck(data, config)
    print("Done!")
