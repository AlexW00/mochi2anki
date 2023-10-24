# Mochi -> Anki Converter

Simple converter script to convert Mochi cards to Anki cards.

## Usage

1. Export a Mochi deck:
  - right click on the deck
  - select `Export`
  - select `Mochi Format`
  - download the file
  - unzip the file
  -  copy the path to the `data.json` file
2. Create a `config.yml` file for the script (see example-config.yml)
3. Run the script with `python3 mochi2anki.py <path-to-config> <path-to-mochi-export>`
4. The script will create a file called `output.apkg` in the current directory

## Limitations

- no support media files or special template fields
- -> only supports basic fields (e.g. text)
