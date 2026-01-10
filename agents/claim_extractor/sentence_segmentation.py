#sentence_segmentation.py
import spacy
from typing import List, Dict

nlp = spacy.load("en_core_web_sm")

import re

NEWSROOM_MARKERS = [
    "BREAKING:",
    "UPDATE:",
    "EXCLUSIVE:",
    "WATCH:",
    "JUST IN:"
]

def normalize_newsroom_markers(text: str) -> str:
    """
    Force sentence breaks after newsroom markers.
    """
    for marker in NEWSROOM_MARKERS:
        # Ensure marker starts a new line and ends a sentence
        text = re.sub(
            rf"(\n\s*)?{marker}",
            f"\n\n{marker}",
            text
        )
    return text


def preprocess_text(text: str) -> List[str]:
    """
    Light preprocessing:
    - Normalize whitespace
    - Preserve punctuation and casing
    - Split into paragraphs
    """
    paragraphs = [
        p.strip()
        for p in text.split("\n\n")
        if p.strip()
    ]
    return paragraphs


def sentence_segmentation(text: str) -> List[Dict]:
    """
    Step 1 pipeline:
    - Paragraph-aware sentence segmentation
    - Metadata preservation
    """

    text = normalize_newsroom_markers(text)
    paragraphs = preprocess_text(text)
    sentence_records = []

    global_sentence_id = 0
    char_offset = 0

    for para_index, paragraph in enumerate(paragraphs):
        doc = nlp(paragraph)

        for sent in doc.sents:
            sentence_text = sent.text.strip()

            # Skip empty or meaningless sentences
            if not sentence_text:
                continue

            record = {
                "sentence_id": global_sentence_id,
                "text": sentence_text,
                "paragraph_index": para_index,
                "char_start": char_offset + sent.start_char,
                "char_end": char_offset + sent.end_char,
                "contains_quote": '"' in sentence_text or "“" in sentence_text or "”" in sentence_text,
            }

            sentence_records.append(record)
            global_sentence_id += 1

        # Update character offset (+2 for paragraph breaks)
        char_offset += len(paragraph) + 2

    return post_process_fragments(sentence_records)


def post_process_fragments(sentences: List[Dict]) -> List[Dict]:
    """
    Light post-processing:
    - Merge very short journalistic fragments like:
      "However.", "Meanwhile.", "But."
    """
    if not sentences:
        return sentences

    merged = []
    buffer = sentences[0]

    for current in sentences[1:]:
        if len(current["text"]) < 12:
            # Merge fragment into previous sentence
            buffer["text"] = buffer["text"] + " " + current["text"]
            buffer["char_end"] = current["char_end"]
            buffer["contains_quote"] = buffer["contains_quote"] or current["contains_quote"]
        else:
            merged.append(buffer)
            buffer = current

    merged.append(buffer)
    return merged


# ---------------------------
# Example usage
# ---------------------------
if __name__ == "__main__":
    sample_text = """
    The finance minister said the economy grew by 7.2% last year.
    However, experts have disputed the figures.

    "We are confident of sustained growth," the minister added.
    BREAKING: Fire breaks out in Mumbai. Rescue operations underway.
    """

    sentences = sentence_segmentation(sample_text)

    for s in sentences:
        print(s)
