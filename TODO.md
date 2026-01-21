# Adding Tests to the NER App - A TODO Guide

This guide will walk you through the process of adding unit tests to the `ner_app` to make it more robust and reliable. We'll be using the `pytest` framework for our tests.

## 1. Create a `tests` directory

First, you need to create a directory to hold your test files. This is a standard convention in Python projects.

```bash
mkdir tests
```

## 2. Add `pytest` to your `requirements.txt`

We need to add `pytest` to our project's dependencies. Open `ner_app/requirements.txt` and add the following line at the end:

```
pytest>=7.0.0
```

After adding it, you should install the new dependency:

```bash
pip install -r ner_app/requirements.txt
```

## 3. Create your first test file

Let's start by creating a test file for our `normalizers`. Create a new file called `tests/test_normalizers.py`.

Here is a basic structure for this file with a sample test case to get you started:

```python
# tests/test_normalizers.py

from ner_app.normalizers import normalize_by_type

def test_normalize_by_type_country():
    aliases = {
        "country": {
            "us": ["United States of America"]
        }
    }
    result = normalize_by_type("country", "US", aliases)
    assert len(result) == 1
    assert result[0]["canonical"] == "United States of America"

def test_normalize_by_type_generic():
    aliases = {}
    result = normalize_by_type("organization", "Example Corp", aliases)
    assert len(result) == 1
    assert result[0]["canonical"] == "Example Corp"

```

## 4. Write more tests

Now you can expand on this and create more test files and test cases. Here are some suggestions for other test files and what you could test in them:

### `tests/test_ner_pipeline.py`

This file should contain tests for the core NER pipeline logic.

```python
# tests/test_ner_pipeline.py

from ner_app.ner_pipeline import _calculate_confidence, extract_observations

def test_calculate_confidence():
    # Test the confidence calculation with different weights
    pass

def test_extract_observations():
    # Test the observation extraction with a sample text
    pass

# ... and so on for other functions in ner_pipeline.py
```

### `tests/test_store.py`

This file should contain tests for the database storage logic. You could use an in-memory SQLite database for these tests to avoid creating actual files.

```python
# tests/test_store.py

import sqlite3
from ner_app.store import ensure_schema, upsert_datamodel, insert_observation

def test_database_operations():
    conn = sqlite3.connect(":memory:")
    ensure_schema(conn)

    # Test upsert_datamodel
    # Test insert_observation

    conn.close()

```

## 5. Run your tests

Once you have written your tests, you can run them from the root of your project directory using the following command:

```bash
python -m pytest
```

`pytest` will automatically discover and run all the tests in the `tests` directory.

Good luck, and have fun!
