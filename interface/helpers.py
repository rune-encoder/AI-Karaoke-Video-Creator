# Standard Library Imports
from typing import List, Union
from pathlib import Path
import json
import logging

# Initialize logger
logger = logging.getLogger(__name__)


# Helper Functions
def display_lyrics_format(json_file: Union[str, Path]) -> str:
    """
    Groups words by verse and returns a user-friendly multiline string.
    """
    try:
        with open(json_file, "r") as f:
            metadata = json.load(f)

        # Group words by verse for display
        grouped_by_verse = {}
        for verse_info in metadata:
            verse_number = verse_info["verse_number"]
            if verse_number not in grouped_by_verse:
                grouped_by_verse[verse_number] = []
            for w in verse_info.get("words", []):
                grouped_by_verse[verse_number].append(w["word"])

        # Create display text for the verses
        verse_texts = []
        for verse_num, words_list in grouped_by_verse.items():
            line = " ".join(words_list)
            verse_texts.append(f"Verse {verse_num}: {line}")

        # Join them with newlines
        display_text = "\n".join(verse_texts)
        return display_text
    
    except Exception as e:
        logger.error(f"Error generating display lyrics: {e}")
        return f"Error: {e}"


def load_json_file(file_path: Union[str, Path]) -> Union[List, dict, None]:
    """
    Safely loads a JSON file into Python data structure.
    Returns None if file not found or error.
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Could not load JSON file {file_path}: {e}")
        return None


def save_json_file(data, file_path: Union[str, Path]):
    """
    Save Python data structure as a JSON file.
    Overwrites if file exists.
    """
    try:
        file_path = Path(file_path)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        logger.error(f"Could not save JSON to {file_path}: {e}")
        raise
