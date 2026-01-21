import json
import spacy

from ner_app.config import (
    ALIASES_PATH,
    DATAMODEL_PATH,
    MODEL,
    BASE_CONFIDENCE,
    CONFIDENCE_WEIGHTS,
    AMBIGUITY_PENALTY,
)
from ner_app.normalizers import normalize_by_type


def load_datamodel(path=DATAMODEL_PATH):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)["fields"]


def load_aliases(path=ALIASES_PATH):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_spacy_model(model_name=MODEL):
    return spacy.load(model_name)


def _build_label_map(fields):
    label_map = {}
    for field in fields:
        for label in field["entity_types"]:
            label_map.setdefault(label, []).append(field)
    return label_map


def _base_confidence(ent):
    confidence = BASE_CONFIDENCE
    if hasattr(ent._, "confidence"):
        try:
            confidence = float(ent._.confidence)
        except (TypeError, ValueError):
            pass
    return confidence


def _calculate_confidence(base_conf, alias_confidence, ambiguous, normalizer_name):
    weights = CONFIDENCE_WEIGHTS.get(normalizer_name, CONFIDENCE_WEIGHTS["default"])
    combined = (base_conf * weights["base"]) + (alias_confidence * weights["alias"])
    if ambiguous:
        combined = max(0.0, combined - AMBIGUITY_PENALTY)
    return combined


def extract_observations(text, source, fields, aliases, nlp):
    label_map = _build_label_map(fields)
    doc = nlp(text)
    observations = []

    for ent in doc.ents:
        for field in label_map.get(ent.label_, []):
            base_conf = _base_confidence(ent)
            normalizer_name = field["normalizer"]
            candidates = normalize_by_type(normalizer_name, ent.text, aliases)

            for candidate in candidates:
                combined = _calculate_confidence(
                    base_conf,
                    candidate["alias_confidence"],
                    candidate.get("ambiguous"),
                    normalizer_name,
                )

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
