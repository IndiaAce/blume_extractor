import json
import sqlite3
from datetime import datetime


SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS datamodel_fields (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        entity_types TEXT NOT NULL,
        normalizer TEXT NOT NULL,
        min_confidence REAL NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS observations (
        id INTEGER PRIMARY KEY,
        field_id INTEGER NOT NULL,
        raw_text TEXT NOT NULL,
        canonical_value TEXT NOT NULL,
        confidence REAL NOT NULL,
        source TEXT,
        context TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(field_id) REFERENCES datamodel_fields(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS aliases (
        alias TEXT NOT NULL,
        canonical TEXT NOT NULL,
        type TEXT NOT NULL,
        confidence REAL NOT NULL,
        UNIQUE(alias, canonical, type)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS overrides (
        field_id INTEGER NOT NULL,
        raw_text TEXT NOT NULL,
        canonical_value TEXT NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE(field_id, raw_text)
    )
    """,
]


def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(conn):
    for statement in SCHEMA_STATEMENTS:
        conn.execute(statement)
    conn.commit()


def upsert_datamodel(conn, fields):
    field_ids = {}
    for field in fields:
        conn.execute(
            """
            INSERT OR IGNORE INTO datamodel_fields (name, entity_types, normalizer, min_confidence)
            VALUES (?, ?, ?, ?)
            """,
            (
                field["name"],
                json.dumps(field["entity_types"]),
                field["normalizer"],
                field["min_confidence"],
            ),
        )
        row = conn.execute(
            "SELECT id FROM datamodel_fields WHERE name = ?",
            (field["name"],),
        ).fetchone()
        if row:
            field_ids[field["name"]] = row["id"]

    conn.commit()
    return field_ids


def insert_observation(conn, field_id, raw_text, canonical_value, confidence, source, context=None):
    conn.execute(
        """
        INSERT INTO observations (
            field_id,
            raw_text,
            canonical_value,
            confidence,
            source,
            context,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            field_id,
            raw_text,
            canonical_value,
            float(confidence),
            source,
            context,
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
