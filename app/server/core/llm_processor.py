import os
from typing import Dict, Any
from openai import OpenAI
from anthropic import Anthropic
from core.data_models import QueryRequest


def generate_sql_with_openai(query_text: str, schema_info: Dict[str, Any]) -> str:
    """
    Generate SQL query using OpenAI API
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        client = OpenAI(api_key=api_key)

        # Format schema for prompt
        schema_description = format_schema_for_prompt(schema_info)

        # Create prompt
        prompt = f"""Given the following database schema:

{schema_description}

Convert this natural language query to SQL: "{query_text}"

Rules:
- Return ONLY the SQL query, no explanations
- Use proper SQLite syntax
- Handle date/time queries appropriately (e.g., "last week" = date('now', '-7 days'))
- Be careful with column names and table names
- If the query is ambiguous, make reasonable assumptions
- For multi-table queries, use proper JOIN conditions to avoid Cartesian products
- Limit results to reasonable amounts (e.g., add LIMIT 100 for large result sets)
- When joining tables, use meaningful relationships between tables
- NEVER include SQL comments (-- or /* */) in the query

SQL Query:"""

        # Call OpenAI API
        # Note: o4-mini model requires max_completion_tokens instead of max_tokens
        # and only supports temperature=1.0 (default)
        response = client.chat.completions.create(
            model="o4-mini-2025-04-16",
            messages=[
                {
                    "role": "system",
                    "content": "You are a SQL expert. Convert natural language to SQL queries.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=1.0,
            max_completion_tokens=500,
        )

        sql = response.choices[0].message.content.strip()

        # Clean up the SQL (remove markdown if present)
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]

        return sql.strip()

    except Exception as e:
        raise Exception(f"Error generating SQL with OpenAI: {str(e)}")


def generate_sql_with_anthropic(query_text: str, schema_info: Dict[str, Any]) -> str:
    """
    Generate SQL query using Anthropic API
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        client = Anthropic(api_key=api_key)

        # Format schema for prompt
        schema_description = format_schema_for_prompt(schema_info)

        # Create prompt
        prompt = f"""Given the following database schema:

{schema_description}

Convert this natural language query to SQL: "{query_text}"

Rules:
- Return ONLY the SQL query, no explanations
- Use proper SQLite syntax
- Handle date/time queries appropriately (e.g., "last week" = date('now', '-7 days'))
- Be careful with column names and table names
- If the query is ambiguous, make reasonable assumptions
- For multi-table queries, use proper JOIN conditions to avoid Cartesian products
- Limit results to reasonable amounts (e.g., add LIMIT 100 for large result sets)
- When joining tables, use meaningful relationships between tables
- NEVER include SQL comments (-- or /* */) in the query

SQL Query:"""

        # Call Anthropic API
        response = client.messages.create(
            model="claude-sonnet-4-0",
            max_tokens=500,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}],
        )

        sql = response.content[0].text.strip()

        # Clean up the SQL (remove markdown if present)
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]

        return sql.strip()

    except Exception as e:
        raise Exception(f"Error generating SQL with Anthropic: {str(e)}")


def format_schema_for_prompt(schema_info: Dict[str, Any]) -> str:
    """
    Format database schema for LLM prompt
    """
    lines = []

    for table_name, table_info in schema_info.get("tables", {}).items():
        lines.append(f"Table: {table_name}")
        lines.append("Columns:")

        for col_name, col_type in table_info["columns"].items():
            lines.append(f"  - {col_name} ({col_type})")

        lines.append(f"Row count: {table_info['row_count']}")
        lines.append("")

    return "\n".join(lines)


def generate_random_query_with_openai(schema_info: Dict[str, Any]) -> str:
    """
    Generate a random natural language query using OpenAI API
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        client = OpenAI(api_key=api_key)

        # Format schema for prompt
        schema_description = format_schema_for_prompt(schema_info)

        # Create prompt
        prompt = f"""Given the following database schema:

{schema_description}

Generate an interesting natural language query that someone might ask about this data. 
The query should be:
- Contextually relevant to the table structures and columns
- Natural and conversational
- Maximum two sentences
- Something that would demonstrate the capability of natural language to SQL conversion
- Varied in complexity (sometimes simple, sometimes complex with JOINs or aggregations)
- Do NOT include any SQL syntax, comments, or special characters
- Focus primarily on single table queries unless explicitly asked for a multi-table query

Examples of good queries:
- "What are the top 5 products by revenue?"
- "Show me all customers who ordered in the last month."
- "Which employees have the highest average sales? List their names and departments."

Natural language query:"""

        # Call OpenAI API
        # Note: o4-mini model requires max_completion_tokens instead of max_tokens
        # and only supports temperature=1.0 (default)
        response = client.chat.completions.create(
            model="o4-mini-2025-04-16",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates interesting questions about data.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        query = response.choices[0].message.content

        if query is None:
            query = ""
        else:
            query = query.strip()

        print(f"DEBUG: Final query after processing: '{query}'")
        return query

    except Exception as e:
        raise Exception(f"Error generating random query with OpenAI: {str(e)}")


def generate_random_query_with_anthropic(schema_info: Dict[str, Any]) -> str:
    """
    Generate a random natural language query using Anthropic API
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        client = Anthropic(api_key=api_key)

        # Format schema for prompt
        schema_description = format_schema_for_prompt(schema_info)

        # Create prompt
        prompt = f"""Given the following database schema:

{schema_description}

Generate an interesting natural language query that someone might ask about this data. 
The query should be:
- Contextually relevant to the table structures and columns
- Natural and conversational
- Maximum two sentences
- Something that would demonstrate the capability of natural language to SQL conversion
- Varied in complexity (sometimes simple, sometimes complex with JOINs or aggregations)
- Do NOT include any SQL syntax, comments, or special characters

Examples of good queries:
- "What are the top 5 products by revenue?"
- "Show me all customers who ordered in the last month."
- "Which employees have the highest average sales? List their names and departments."

Natural language query:"""

        # Call Anthropic API
        response = client.messages.create(
            model="claude-sonnet-4-0",
            max_tokens=100,
            temperature=0.8,
            messages=[{"role": "user", "content": prompt}],
        )

        query = response.content[0].text.strip()
        return query

    except Exception as e:
        raise Exception(f"Error generating random query with Anthropic: {str(e)}")


def generate_random_query(schema_info: Dict[str, Any]) -> str:
    """
    Route to appropriate LLM provider for random query generation
    Priority: 1) OpenAI API key exists, 2) Anthropic API key exists
    """
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    # Check API key availability (OpenAI priority)
    if openai_key:
        return generate_random_query_with_openai(schema_info)
    elif anthropic_key:
        return generate_random_query_with_anthropic(schema_info)
    else:
        raise ValueError(
            "No LLM API key found. Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY"
        )


def generate_abap_with_openai(query_text: str, schema_info: Dict[str, Any]) -> str:
    """
    (Claude)
    Generate ABAP code using OpenAI API
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        client = OpenAI(api_key=api_key)

        # Format schema for prompt - translate to SAP concepts
        schema_description = format_schema_for_abap_prompt(schema_info)

        # Create prompt for ABAP generation
        prompt = f"""Given the following SAP database schema:

{schema_description}

Convert this natural language query to ABAP code: "{query_text}"

Rules:
- Return ONLY the ABAP code, no explanations or markdown formatting
- Use proper ABAP syntax for SAP systems
- Use standard ABAP naming conventions (lv_ for local variables, lt_ for internal tables, ls_ for structures)
- Declare internal tables with TYPE TABLE OF
- Use SELECT statements to retrieve data from SAP tables
- Store results in internal tables
- Include proper DATA declarations
- Use proper WHERE clause construction to avoid SQL injection
- Add LIMIT clause for large result sets
- Do NOT include comments in the code
- Format with proper indentation
- Handle date/time fields using SAP date formats (YYYYMMDD)
- For multi-table queries, use proper JOIN syntax

Example ABAP structure:
DATA: lt_results TYPE TABLE OF <table_name>,
      ls_result TYPE <table_name>.

SELECT * FROM <table_name>
  INTO TABLE lt_results
  WHERE <conditions>
  ORDER BY <fields>
  UP TO 100 ROWS.

ABAP Code:"""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="o4-mini-2025-04-16",
            messages=[
                {
                    "role": "system",
                    "content": "You are an ABAP expert for SAP systems. Convert natural language to ABAP code.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=1.0,
            max_completion_tokens=800,
        )

        abap = response.choices[0].message.content.strip()

        # Clean up the ABAP (remove markdown if present)
        if abap.startswith("```abap"):
            abap = abap[7:]
        if abap.startswith("```"):
            abap = abap[3:]
        if abap.endswith("```"):
            abap = abap[:-3]

        return abap.strip()

    except Exception as e:
        raise Exception(f"Error generating ABAP with OpenAI: {str(e)}")


def generate_abap_with_anthropic(query_text: str, schema_info: Dict[str, Any]) -> str:
    """
    (Claude)
    Generate ABAP code using Anthropic API
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        client = Anthropic(api_key=api_key)

        # Format schema for prompt - translate to SAP concepts
        schema_description = format_schema_for_abap_prompt(schema_info)

        # Create prompt for ABAP generation
        prompt = f"""Given the following SAP database schema:

{schema_description}

Convert this natural language query to ABAP code: "{query_text}"

Rules:
- Return ONLY the ABAP code, no explanations or markdown formatting
- Use proper ABAP syntax for SAP systems
- Use standard ABAP naming conventions (lv_ for local variables, lt_ for internal tables, ls_ for structures)
- Declare internal tables with TYPE TABLE OF
- Use SELECT statements to retrieve data from SAP tables
- Store results in internal tables
- Include proper DATA declarations
- Use proper WHERE clause construction to avoid SQL injection
- Add LIMIT clause for large result sets
- Do NOT include comments in the code
- Format with proper indentation
- Handle date/time fields using SAP date formats (YYYYMMDD)
- For multi-table queries, use proper JOIN syntax

Example ABAP structure:
DATA: lt_results TYPE TABLE OF <table_name>,
      ls_result TYPE <table_name>.

SELECT * FROM <table_name>
  INTO TABLE lt_results
  WHERE <conditions>
  ORDER BY <fields>
  UP TO 100 ROWS.

ABAP Code:"""

        # Call Anthropic API
        response = client.messages.create(
            model="claude-sonnet-4-0",
            max_tokens=800,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}],
        )

        abap = response.content[0].text.strip()

        # Clean up the ABAP (remove markdown if present)
        if abap.startswith("```abap"):
            abap = abap[7:]
        if abap.startswith("```"):
            abap = abap[3:]
        if abap.endswith("```"):
            abap = abap[:-3]

        return abap.strip()

    except Exception as e:
        raise Exception(f"Error generating ABAP with Anthropic: {str(e)}")


def format_schema_for_abap_prompt(schema_info: Dict[str, Any]) -> str:
    """
    (Claude)
    Format database schema for ABAP LLM prompt, translating to SAP concepts
    """
    lines = []

    for table_name, table_info in schema_info.get("tables", {}).items():
        # Convert table name to SAP Z-table convention
        sap_table_name = f"Z{table_name.upper()}" if not table_name.startswith("Z") else table_name.upper()
        lines.append(f"SAP Table: {sap_table_name}")
        lines.append("Fields:")

        for col_name, col_type in table_info["columns"].items():
            # Map SQLite types to ABAP types
            abap_type = map_sql_type_to_abap(col_type)
            lines.append(f"  - {col_name.upper()} ({abap_type})")

        lines.append(f"Approximate rows: {table_info['row_count']}")
        lines.append("")

    return "\n".join(lines)


def map_sql_type_to_abap(sql_type: str) -> str:
    """
    (Claude)
    Map SQL data types to ABAP data types
    """
    sql_type_upper = sql_type.upper()

    if "INT" in sql_type_upper:
        return "INT4"
    elif "TEXT" in sql_type_upper or "VARCHAR" in sql_type_upper or "CHAR" in sql_type_upper:
        return "CHAR"
    elif "REAL" in sql_type_upper or "FLOAT" in sql_type_upper or "DOUBLE" in sql_type_upper:
        return "FLTP"
    elif "DATE" in sql_type_upper:
        return "DATS"
    elif "TIME" in sql_type_upper:
        return "TIMS"
    elif "BOOL" in sql_type_upper:
        return "CHAR1"
    else:
        return "CHAR"


def generate_code(request: QueryRequest, schema_info: Dict[str, Any]) -> str:
    """
    (Claude)
    Route to SQL or ABAP generation based on output_mode
    """
    if request.output_mode == "abap":
        # Generate ABAP code
        openai_key = os.environ.get("OPENAI_API_KEY")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

        if openai_key:
            return generate_abap_with_openai(request.query, schema_info)
        elif anthropic_key:
            return generate_abap_with_anthropic(request.query, schema_info)
        else:
            raise ValueError(
                "No LLM API key found. Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY"
            )
    else:
        # Generate SQL (default)
        return generate_sql_internal(request, schema_info)


def generate_sql_internal(request: QueryRequest, schema_info: Dict[str, Any]) -> str:
    """
    (Claude)
    Internal SQL generation with routing logic
    """
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    # Check API key availability first (OpenAI priority)
    if openai_key:
        return generate_sql_with_openai(request.query, schema_info)
    elif anthropic_key:
        return generate_sql_with_anthropic(request.query, schema_info)

    # Fall back to request preference if both keys available or neither available
    if request.llm_provider == "openai":
        return generate_sql_with_openai(request.query, schema_info)
    else:
        return generate_sql_with_anthropic(request.query, schema_info)


def generate_sql(request: QueryRequest, schema_info: Dict[str, Any]) -> str:
    """
    Route to appropriate LLM provider based on API key availability and request preference.
    Priority: 1) OpenAI API key exists, 2) Anthropic API key exists, 3) request.llm_provider
    Backward compatibility wrapper that delegates to generate_code
    """
    return generate_code(request, schema_info)
