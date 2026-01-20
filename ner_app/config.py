import os


DEFAULT_MODEL = os.environ.get("NER_SPACY_MODEL", "en_core_web_sm")
DEFAULT_DB_PATH = os.environ.get("NER_DB_PATH", "ner_app/ner.db")
DEFAULT_DATAMODEL_PATH = os.environ.get("NER_DATAMODEL_PATH", "ner_app/datamodel.json")
DEFAULT_ALIASES_PATH = os.environ.get("NER_ALIASES_PATH", "ner_app/aliases.json")
