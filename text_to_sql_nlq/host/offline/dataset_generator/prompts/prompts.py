QUESTION_PROMPT = """
Schema:

{metadata}

Generate exactly {count}
Text-to-SQL questions.

Return ONLY valid JSON.

Do NOT:
- add explanations
- add markdown
- wrap in ```json
"""


RETRIEVAL_PROMPT = """
Schema:

{metadata}

Question:

{question}

Return expected tables.

Return ONLY valid JSON in exactly this format:

{{
    "expected_tables": [
        "table1",
        "table2"
    ]
}}

Rules:
- Include only necessary tables.
- Do not add explanations.
- Do not return markdown.
- Do not wrap in ```json.
- Do not return any additional fields.
"""


SQL_PROMPT = """
Schema:

{metadata}

Question:

{question}

Tables:

{tables}

Generate SQL.

Return ONLY valid JSON in exactly this format:

{{
    "gold_sql": "SELECT ..."
}}

Do NOT:
- add explanations
- add markdown
- wrap in ```json
"""