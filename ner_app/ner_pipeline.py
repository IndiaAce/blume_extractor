import json

import spacy

from ner_app.config import (
    DEFAULT_ALIASES_PATH,
    DEFAULT_DATAMODEL_PATH,
    DEFAULT_MODEL,
)
from ner_app.normalizers import normalize_by_type


DEFAULT_BASE_CONFIDENCE = 0.55


def load_datamodel(path=DEFAULT_DATAMODEL_PATH):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)["fields"]


def load_aliases(path=DEFAULT_ALIASES_PATH):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_spacy_model(model_name=DEFAULT_MODEL):
    return spacy.load(model_name)


def _build_label_map(fields):
    label_map = {}
    for field in fields:
        for label in field["entity_types"]:
            label_map.setdefault(label, []).append(field)
    return label_map


def _base_confidence(ent):
    confidence = DEFAULT_BASE_CONFIDENCE
    if hasattr(ent._, "confidence"):
        try:
            confidence = float(ent._.confidence)
        except (TypeError, ValueError):
            pass
    return confidence


def extract_observations(text, source, fields, aliases, nlp):
    label_map = _build_label_map(fields)
    doc = nlp(text)
    observations = []

    for ent in doc.ents:
        for field in label_map.get(ent.label_, []):
            base_conf = _base_confidence(ent)
            candidates = normalize_by_type(field["normalizer"], ent.text, aliases)

            for candidate in candidates:
                combined = (base_conf * 0.6) + (candidate["alias_confidence"] * 0.4)
                if candidate.get("ambiguous"):
                    combined = max(0.0, combined - 0.1)

                if combined < field["min_confidence"]:
                    continue

                observations.append(
                    {
                        "field_name": field["name"],
                        "raw_text": ent.text,
                        "canonical": candidate["canonical"],
                        "confidence": round(combined, 4),
                        "source": source,
                        "context": ent.sent.text if ent.sent is not None else None,
                    }
                )

    return observations
