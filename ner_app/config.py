import os
import yaml

DEFAULT_CONFIG_PATH = os.environ.get("NER_CONFIG_PATH", "ner_app/config.yaml")


def load_config(path=DEFAULT_CONFIG_PATH):
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


config = load_config()

# Get settings from the config file, with fallbacks to the old environment variables or defaults
MODEL = config.get("model", os.environ.get("NER_SPACY_MODEL", "en_core_web_sm"))
DB_PATH = config.get("db_path", os.environ.get("NER_DB_PATH", "ner_app/ner.db"))
DATAMODEL_PATH = config.get("datamodel_path", os.environ.get("NER_DATAMODEL_PATH", "ner_app/datamodel.json"))
ALIASES_PATH = config.get("aliases_path", os.environ.get("NER_ALIASES_PATH", "ner_app/aliases.json"))
BASE_CONFIDENCE = config.get("base_confidence", 0.55)
CONFIDENCE_WEIGHTS = config.get(
    "confidence_weights",
    {"default": {"base": 0.6, "alias": 0.4}},
)
AMBIGUITY_PENALTY = config.get("ambiguity_penalty", 0.1)
LOGGING_CONFIG = config.get("logging", {"level": "INFO"})