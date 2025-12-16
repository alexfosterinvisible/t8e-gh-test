# NLP to ABAP SAP Code Conversion

**ADW ID:** 6b5c2c81
**Date:** 2025-12-16
**Specification:** specs/issue-13-adw-6b5c2c81-sdlc_planner-nlp-to-abap-conversion.md

## Overview

This feature extends the Natural Language SQL Interface application to support ABAP code generation for SAP systems. Users can now toggle between SQL and ABAP output modes, enabling SAP developers to quickly generate ABAP code snippets from natural language queries without manually writing syntax. The ABAP code is displayed for reference but not executed, as ABAP execution requires SAP system connectivity.

## What Was Built

- UI toggle for switching between SQL and ABAP output modes
- Backend ABAP code generation using OpenAI and Anthropic LLM providers
- Schema translation from SQLite concepts to SAP table concepts
- Frontend integration to display ABAP code with appropriate messaging
- Comprehensive unit tests for ABAP generation functions
- End-to-end test specification for ABAP conversion workflow
- Updated documentation explaining the new feature

## Technical Implementation

### Files Modified

- `app/server/core/data_models.py`: Added `output_mode` field to `QueryRequest` model (Literal["sql", "abap"], defaults to "sql") and `code`/`output_mode` fields to `QueryResponse` model for backward compatibility
- `app/server/core/llm_processor.py`: Implemented `generate_abap_with_openai()`, `generate_abap_with_anthropic()`, `format_schema_for_abap_prompt()`, `map_sql_type_to_abap()`, and `generate_code()` routing function (234 new lines)
- `app/server/server.py`: Updated `/api/query` endpoint to handle ABAP mode, skip execution for ABAP, and return appropriate responses
- `app/client/index.html`: Added output mode toggle UI with SQL/ABAP buttons
- `app/client/src/main.ts`: Implemented output mode state management, toggle event handlers, and updated query execution to include output mode
- `app/client/src/api/client.ts`: Updated API client to send `output_mode` parameter in query requests
- `app/client/src/style.css`: Added styling for mode toggle buttons with active states
- `README.md`: Updated Features, Usage, Output Modes, and API Endpoints sections to document ABAP conversion
- `.claude/commands/e2e/test_abap_conversion.md`: Created E2E test specification with 16 steps and 6+ screenshot requirements
- `app/server/tests/test_abap_generation.py`: Created comprehensive unit tests (225 lines) covering ABAP generation, schema translation, and routing logic
- `app/server/tests/test_data_models.py`: Created data model tests (98 lines) validating new output mode fields

### Key Changes

- **Backend Architecture**: Extended existing LLM processor pattern to support ABAP generation alongside SQL, maintaining the same API key priority logic (OpenAI first, then Anthropic fallback)
- **Schema Translation**: Implemented mapping from SQLite data types to ABAP types (INTEGER → INT4, TEXT → CHAR, DATE → DATS, BOOLEAN → ABAP_BOOL) and table naming conventions (e.g., "users" → "ZUSERS")
- **ABAP Prompt Engineering**: Crafted detailed prompts instructing LLMs to generate production-quality ABAP code following SAP conventions including proper DATA declarations, SELECT statements, internal table usage, and ABAP naming conventions (lv_ for local variables, lt_ for internal tables)
- **Execution Handling**: Added conditional logic to skip query execution when output mode is "abap", returning empty results with informational message
- **Frontend State Management**: Implemented global output mode state with toggle button event handlers and UI updates to reflect active mode

## How to Use

1. **Start the Application**: Run `./run.sh` to start both backend and frontend services
2. **Upload Data**: Drag and drop a CSV or JSON file, or use sample data buttons
3. **Toggle to ABAP Mode**: Click the "ABAP" button in the output mode toggle (above the query input)
4. **Enter Query**: Type a natural language query like "Show me all users from the users table"
5. **View ABAP Code**: Click the Query button (or press Cmd/Ctrl+Enter) to generate ABAP code
6. **Review Output**: The generated ABAP code is displayed with a message indicating it's informational only
7. **Switch Back to SQL**: Click the "SQL" button to return to SQL mode for executable queries

## Configuration

No additional configuration required. The feature uses existing environment variables:

- `OPENAI_API_KEY`: OpenAI API key for ABAP generation (primary)
- `ANTHROPIC_API_KEY`: Anthropic API key for ABAP generation (fallback)

The output mode defaults to "sql" for backward compatibility.

## Testing

### Unit Tests
```bash
cd app/server
uv run pytest tests/test_abap_generation.py -v  # Run ABAP generation tests
uv run pytest tests/test_data_models.py -v      # Run data model tests
uv run pytest                                   # Run all tests
```

### E2E Test
```bash
# Follow the E2E test specification in .claude/commands/e2e/test_abap_conversion.md
# to manually validate the complete ABAP conversion workflow
```

### Key Test Coverage
- ABAP code generation for simple and complex queries
- Schema translation from SQL to ABAP concepts
- OpenAI and Anthropic provider functionality
- Markdown cleanup in ABAP output
- Routing logic between SQL and ABAP modes
- Data model validation for output_mode field
- Error handling for missing API keys

## Notes

### ABAP Code Quality

The LLM-generated ABAP code follows SAP best practices:
- Proper ABAP syntax with SELECT, DATA, INTO TABLE statements
- Standard naming conventions (lv_, lt_, ls_ prefixes)
- Internal table declarations with TYPE TABLE OF
- WHERE clause construction to avoid SQL injection
- LIMIT/UP TO clauses for large result sets
- Proper indentation and formatting

### Limitations

- **No Execution**: ABAP code is displayed but not executed (requires SAP system connectivity)
- **Informational Only**: The feature is designed for code generation assistance, not live SAP integration
- **Schema Mapping**: Schema information is translated from SQLite to SAP concepts, which may not perfectly match actual SAP table structures

### Future Enhancements

Possible future improvements mentioned in the specification:
- ABAP execution via RFC connection to SAP systems
- ABAP syntax validation (client-side or server-side)
- ABAP template library for common patterns
- SAP version selection (ECC, S/4HANA)
- Export functionality for .abap files
- Advanced syntax highlighting using Monaco Editor or Prism.js

### Backward Compatibility

The implementation maintains full backward compatibility:
- `output_mode` defaults to "sql" when not specified
- `QueryResponse.sql` field is maintained alongside the new `code` field
- Existing SQL functionality is completely unchanged
- All existing tests continue to pass
