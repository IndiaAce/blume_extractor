import argparse

from ner_app.config import (
    DEFAULT_ALIASES_PATH,
    DEFAULT_DATAMODEL_PATH,
    DEFAULT_DB_PATH,
    DEFAULT_MODEL,
)
from ner_app.ner_pipeline import extract_observations, load_aliases, load_datamodel, load_spacy_model
from ner_app.store import connect, ensure_schema, insert_observation, upsert_datamodel


def _read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def main():
    parser = argparse.ArgumentParser(description="Run NER and store observations.")
    parser.add_argument("--text", help="Text to analyze.")
    parser.add_argument("--file", help="Path to a text file to analyze.")
    parser.add_argument("--source", default="unknown", help="Source label for the text.")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="SQLite database path.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="spaCy model name.")
    parser.add_argument("--datamodel", default=DEFAULT_DATAMODEL_PATH, help="Datamodel JSON path.")
    parser.add_argument("--aliases", default=DEFAULT_ALIASES_PATH, help="Alias JSON path.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")

    args = parser.parse_args()

    if not args.text and not args.file:
        parser.error("Provide --text or --file.")

    text = args.text if args.text else _read_text(args.file)

    fields = load_datamodel(args.datamodel)
    aliases = load_aliases(args.aliases)
    nlp = load_spacy_model(args.model)

    observations = extract_observations(text, args.source, fields, aliases, nlp)

    conn = connect(args.db_path)
    ensure_schema(conn)
    field_ids = upsert_datamodel(conn, fields)

    for obs in observations:
        field_id = field_ids.get(obs["field_name"])
        if field_id is None:
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

    print(f"Stored {len(observations)} observation(s).")


if __name__ == "__main__":
    main()
