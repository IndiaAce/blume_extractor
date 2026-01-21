import argparse
import logging

from ner_app.config import DB_PATH, DEFAULT_CONFIG_PATH, LOGGING_CONFIG
from ner_app.ner_pipeline import (
    extract_observations,
    load_aliases,
    load_datamodel,
    load_spacy_model,
)
from ner_app.store import connect, ensure_schema, insert_observation, upsert_datamodel


def _read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def main():
    parser = argparse.ArgumentParser(description="Run NER and store observations.")
    parser.add_argument("--text", help="Text to analyze.")
    parser.add_argument("--file", help="Path to a text file to analyze.")
    parser.add_argument("--source", default="unknown", help="Source label for the text.")
    parser.add_argument(
        "--config", default=DEFAULT_CONFIG_PATH, help="Path to config.yaml."
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")

    args = parser.parse_args()

    log_level = LOGGING_CONFIG.get("level", "INFO").upper()
    if args.verbose:
        log_level = "DEBUG"
    logging.basicConfig(level=log_level)

    if not args.text and not args.file:
        parser.error("Provide --text or --file.")

    logging.info("Starting NER pipeline...")
    text = args.text if args.text else _read_text(args.file)

    logging.info("Loading data model, aliases, and spaCy model...")
    fields = load_datamodel()
    aliases = load_aliases()
    nlp = load_spacy_model()

    logging.info("Extracting observations...")
    observations = extract_observations(text, args.source, fields, aliases, nlp)
    logging.info(f"Found {len(observations)} observation(s).")

    logging.info("Storing observations in the database...")
    conn = connect(DB_PATH)
    ensure_schema(conn)
    field_ids = upsert_datamodel(conn, fields)

    for obs in observations:
        field_id = field_ids.get(obs["field_name"])
        if field_id is None:
            logging.warning(
                f"Field name '{obs['field_name']}' not found in the datamodel. Skipping observation."
            )
            continue
        insert_observation(
            conn,
            field_id,
            obs["raw_text"],
            obs["canonical"],
            obs["confidence"],
            obs["source"],
            obs["context"],
        )

    logging.info(f"Stored {len(observations)} observation(s).")
    logging.info("NER pipeline finished.")


if __name__ == "__main__":
    main()
