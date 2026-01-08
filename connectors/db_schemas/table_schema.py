"""
Store schemas for tables to help with construction of queries
"""

class TablesSchema:

    postgres_metadata_schema = """(
        id SERIAL PRIMARY KEY,
        query TEXT,
        issue TEXT,
        severity INTEGER,
        createdate DATE,
        status TEXT,
        resolutiondate Date
    )"""

    jira_data_schema = """(
        Issue Type TEXT,
        Key TEXT,
        Summary TEXT,
        Summary TEXT,
        Assignee TEXT,
        Status TEXT,
        Resolution TEXT,
        Created TEXT,
        Resolution Details TEXT,
        Updated Date
    )"""

    user_feedback_schema = """(
        id SERIAL PRIMARY KEY,
        username TEXT,
        feedback TEXT,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        sentiment CHARACTER VARYING(32)
    )"""