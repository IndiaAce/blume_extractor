import re


WHITESPACE_RE = re.compile(r"\s+")


def _normalize_key(text):
    lowered = text.strip().lower()
    lowered = WHITESPACE_RE.sub(" ", lowered)
    return lowered


def _build_candidates(raw_text, canonical_list, base_confidence):
    return [
        {
            "canonical": canonical,
            "alias_confidence": base_confidence,
            "ambiguous": len(canonical_list) > 1,
        }
        for canonical in canonical_list
    ]


def normalize_with_aliases(raw_text, alias_map):
    key = _normalize_key(raw_text)
    if key in alias_map:
        canonical_list = alias_map[key]
        base_confidence = 0.9 if len(canonical_list) == 1 else 0.75
        return _build_candidates(raw_text, canonical_list, base_confidence)

    return [
        {
            "canonical": raw_text.strip(),
            "alias_confidence": 0.5,
            "ambiguous": False,
        }
    ]


def normalize_generic(raw_text):
    return [
        {
            "canonical": raw_text.strip(),
            "alias_confidence": 0.5,
            "ambiguous": False,
        }
    ]


def normalize_by_type(normalizer_name, raw_text, aliases):
    alias_map = aliases.get(normalizer_name)
    if alias_map:
        return normalize_with_aliases(raw_text, alias_map)

    return normalize_generic(raw_text)
