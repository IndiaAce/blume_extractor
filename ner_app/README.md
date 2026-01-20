# NER v0.1 scaffold

This is a minimal scaffold for a dynamic datamodel-driven NER pipeline.
It is intentionally simple so you can iterate fast.

## Files
- datamodel.json: your fields and mapping rules
- aliases.json: alias and canonicalization rules
- ner_pipeline.py: extraction + mapping + normalization
- store.py: SQLite persistence
- cli.py: command-line entry point
- requirements.txt: Python deps

## Quick start
1) Create a virtualenv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r ner_app/requirements.txt
python -m spacy download en_core_web_sm
```

2) Run a single text:

```bash
python ner_app/cli.py --text "APT24 operators in America targeted a bank" --source tweet
```

3) Check the SQLite db:

```bash
sqlite3 ner_app/ner.db "select * from observations limit 5;"
```

## Notes
- `America` is treated as ambiguous between `United States of America` and `North America` in `aliases.json`.
- You can add manual overrides in the `overrides` table later.
