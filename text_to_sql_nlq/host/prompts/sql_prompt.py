# SQL_PROMPT = """Generate SQL only."""
SQL_PROMPT = """You are a SQL generator. Given the question and schema context, output ONLY the SQL query - no prose, no markdown fences.

Question: {question}
Schema: {schema_context}
{error_block}"""

def build_prompt(
    question: str,
    schema_context: dict,
    error: str | None = None
):
    
    print(schema_context)

    tables = "\n".join(
        [
            t["text"]
            for t in schema_context["tables"]
        ]
    )

    relationships = "\n".join(
        [
            str(r)
            for r in schema_context["relationships"]
        ]
    )

    return f"""
You are a SQL expert.

Question:
{question}

Relevant Tables:
{tables}

Relationships:
{relationships}

Return ONLY raw SQL.
Do NOT wrap SQL in markdown.
Do NOT include explanations.

Previous Error:
{error}
"""