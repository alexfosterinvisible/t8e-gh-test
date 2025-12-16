# Feature: NLP to ABAP SAP Code Conversion

## Metadata

issue_number: `13`
adw_id: `6b5c2c81`
issue_json: `{"number":13,"title":"Feature Request: Add NLP to ABAP SAP conversion button","body":"## Feature Request\n\nAdd a button that enables Natural Language Processing (NLP) to ABAP SAP code generation, as an alternative to the existing SQL generation.\n\n### Use Case\nUsers working with SAP systems need the ability to convert natural language queries directly to ABAP code, similar to how the current NLP -> SQL feature works.\n\n### Proposed Solution\nAdd a toggle or separate button in the UI that switches the output target from SQL to ABAP SAP syntax."}`

## Feature Description

This feature adds the capability to convert natural language queries into ABAP SAP code, complementing the existing NLP to SQL conversion functionality. Users will be able to toggle between SQL and ABAP output modes, with the backend generating appropriate ABAP syntax using the same LLM providers (OpenAI/Anthropic) that currently power SQL generation. The UI will display ABAP code instead of SQL, with execution disabled (as ABAP requires SAP system connectivity which is out of scope).

## User Story

As a SAP developer or analyst
I want to convert natural language queries to ABAP SAP code
So that I can quickly generate ABAP code snippets for my SAP development work without manually writing the syntax

## Problem Statement

Currently, the application only supports NLP to SQL conversion. Users working with SAP systems need similar assistance for generating ABAP code but have no built-in tool to convert their natural language requirements into proper ABAP syntax. This creates inefficiency for SAP developers who must manually translate business logic into ABAP code.

## Solution Statement

Extend the existing NLP architecture to support ABAP code generation by:

1. Adding a UI toggle/button to switch between SQL and ABAP output modes
2. Implementing ABAP code generation functions in the backend using the existing LLM providers
3. Updating the query flow to route requests to the appropriate code generator based on the selected mode
4. Displaying ABAP code in the results section without execution (informational only)
5. Maintaining backward compatibility with the existing SQL generation functionality

## Relevant Files

Use these files to implement the feature:

- `app/server/core/llm_processor.py` - Contains the SQL generation logic using OpenAI and Anthropic. Will be extended to add ABAP generation functions following the same pattern as `generate_sql_with_openai` and `generate_sql_with_anthropic`.

- `app/server/core/data_models.py` - Defines Pydantic models for API requests and responses. Will be updated to add an output mode field to `QueryRequest` to specify whether the user wants SQL or ABAP output.

- `app/server/server.py` - FastAPI server with the `/api/query` endpoint. Will be updated to handle the new output mode parameter and route to appropriate code generation functions.

- `app/client/src/main.ts` - Main frontend logic including query execution and results display. Will be updated to send the selected output mode with queries and display ABAP code appropriately.

- `app/client/src/api/client.ts` - API client for backend communication. Will be updated to include the output mode in query requests.

- `app/client/index.html` - HTML structure of the application. Will be updated to add a toggle/button for switching between SQL and ABAP modes.

- `app/client/src/style.css` - Styling for the application. Will be updated to style the new mode toggle button.

- `README.md` - Project documentation. Will be updated to document the new ABAP conversion feature.

- Read `.claude/commands/conditional_docs.md` - To check if additional documentation is needed based on task conditions.
- Read `.claude/commands/test_e2e.md` - To understand E2E test execution framework.
- Read `.claude/commands/e2e/test_basic_query.md` - To understand E2E test structure and format.

### New Files

- `.claude/commands/e2e/test_abap_conversion.md` - E2E test file to validate the ABAP conversion feature works end-to-end. Will test toggling to ABAP mode, entering a natural language query, and verifying ABAP code is generated and displayed correctly.

- `app/server/tests/test_abap_generation.py` - Unit tests for ABAP code generation functions to ensure the LLM processors generate valid ABAP syntax.

## Implementation Plan

### Phase 1: Foundation

Update backend data models to support output mode selection, allowing the system to distinguish between SQL and ABAP code generation requests. This includes adding a new field to the QueryRequest model and updating the QueryResponse model to handle ABAP code output.

### Phase 2: Core Implementation

Implement ABAP code generation in the backend by creating new functions in llm_processor.py that mirror the SQL generation logic but produce ABAP code instead. Update the query processing endpoint to route requests to the appropriate generator based on the output mode. Add comprehensive prompts for the LLM to generate proper ABAP syntax following SAP conventions.

### Phase 3: Integration

Update the frontend to add a UI toggle for switching between SQL and ABAP modes. Modify the query submission flow to include the selected mode and update the results display to show ABAP code with appropriate syntax highlighting. Ensure the toggle state persists across queries and provides clear visual feedback about which mode is active.

## Step by Step Tasks

IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Update Backend Data Models

- Read `app/server/core/data_models.py` to understand current QueryRequest and QueryResponse structure
- Add `output_mode` field to `QueryRequest` model with type `Literal["sql", "abap"]` and default value `"sql"` for backward compatibility
- Update `QueryResponse` model to change `sql` field to `code` field (or add both for compatibility) to represent either SQL or ABAP code
- Add optional `output_mode` field to `QueryResponse` to echo back which mode was used
- Write unit tests in `app/server/tests/test_data_models.py` (create if doesn't exist) to validate the new fields

### Step 2: Implement ABAP Code Generation Functions

- Read `app/server/core/llm_processor.py` to understand the SQL generation implementation
- Create `generate_abap_with_openai(query_text: str, schema_info: Dict[str, Any]) -> str` function that generates ABAP code using OpenAI
  - Use prompts that instruct the LLM to generate ABAP syntax for SAP systems
  - Include ABAP best practices in the prompt (e.g., SELECT statements, DATA declarations, internal tables)
  - Handle schema information by translating database tables to SAP table concepts
  - Return clean ABAP code without markdown formatting
- Create `generate_abap_with_anthropic(query_text: str, schema_info: Dict[str, Any]) -> str` function that generates ABAP code using Anthropic
  - Follow the same pattern as OpenAI function
  - Use appropriate Anthropic model and parameters
- Create `generate_code(request: QueryRequest, schema_info: Dict[str, Any]) -> str` function that routes to SQL or ABAP generation based on `output_mode`
  - If `output_mode == "sql"`, call existing SQL generation functions
  - If `output_mode == "abap"`, call new ABAP generation functions
  - Maintain the existing API key priority logic (OpenAI first, then Anthropic)
- Update the existing `generate_sql()` function to delegate to the new `generate_code()` function for backward compatibility
- Create comprehensive unit tests in `app/server/tests/test_abap_generation.py` to validate:
  - ABAP code is generated for simple queries
  - ABAP code is generated for complex queries with joins
  - Schema information is properly translated
  - Error handling works correctly
  - Both OpenAI and Anthropic functions work

### Step 3: Update Query Processing Endpoint

- Read `app/server/server.py` to understand the current `/api/query` endpoint implementation
- Update `process_natural_language_query` function to:
  - Accept the new `output_mode` field from the QueryRequest
  - Call the new `generate_code()` function instead of `generate_sql()`
  - Handle ABAP code responses by skipping SQL execution (ABAP cannot be executed without SAP system)
  - Return appropriate response with ABAP code and empty results when mode is "abap"
  - Update logging to indicate which output mode was used
- Add validation to ensure `output_mode` is either "sql" or "abap"
- Update error handling to provide clear messages for ABAP-specific errors
- Update existing tests in `app/server/tests/test_server.py` (create if doesn't exist) to cover both SQL and ABAP modes

### Step 4: Add Frontend UI Toggle

- Read `app/client/index.html` to understand the current layout structure
- Add a toggle button group in the query section (before or after the query input):
  ```html
  <div class="output-mode-toggle">
    <button id="sql-mode-button" class="mode-button active">SQL</button>
    <button id="abap-mode-button" class="mode-button">ABAP</button>
  </div>
  ```
- Read `app/client/src/style.css` to understand the current styling patterns
- Add CSS styling for the toggle button group:
  - Style `.output-mode-toggle` container with flexbox layout
  - Style `.mode-button` with appropriate colors, hover states, and transitions
  - Style `.mode-button.active` to highlight the currently selected mode
  - Ensure the toggle is visually prominent but not intrusive
  - Make it responsive for mobile devices

### Step 5: Update Frontend Query Logic

- Read `app/client/src/main.ts` to understand the current query execution flow
- Add global state variable to track the selected output mode (default: "sql")
- In `initializeQueryInput()` function:
  - Add event listeners to the mode toggle buttons
  - Update the active button class when mode is toggled
  - Store the selected mode in the state variable
- In the `executeQuery()` function within `initializeQueryInput()`:
  - Include the selected output mode in the query request payload sent to the backend
  - Update the API call to `api.processQuery()` to include the output mode
- In `displayResults()` function:
  - Update the label from "SQL:" to dynamically show "SQL:" or "ABAP:" based on the output mode
  - If output mode is ABAP, show a message indicating "ABAP code generated (execution not supported)"
  - Update code display styling to differentiate between SQL and ABAP (consider using different colors or icons)
- Read `app/client/src/api/client.ts` to understand the API client structure
- Update `api.processQuery()` function in `app/client/src/api/client.ts`:
  - Ensure the `QueryRequest` type includes the `output_mode` field
  - Pass the output mode parameter in the request body

### Step 6: Create E2E Test for ABAP Conversion

- Read `.claude/commands/test_e2e.md` to understand how E2E tests are structured and executed
- Read `.claude/commands/e2e/test_basic_query.md` to see an example E2E test format
- Create `.claude/commands/e2e/test_abap_conversion.md` with the following test steps:
  1. Navigate to the application URL
  2. Take screenshot of initial state
  3. Verify the output mode toggle is present with "SQL" and "ABAP" buttons
  4. Verify "SQL" mode is active by default
  5. Click the "ABAP" mode button
  6. Take screenshot showing ABAP mode is active
  7. Enter a natural language query like "Show me all users from the users table"
  8. Take screenshot of the query input with ABAP mode selected
  9. Click the Query button
  10. Verify ABAP code is generated and displayed (should contain ABAP syntax like "SELECT", "FROM", "INTO TABLE")
  11. Take screenshot of the ABAP code output
  12. Verify that no results table is shown (ABAP execution not supported)
  13. Verify a message indicates ABAP code is informational only
  14. Switch back to SQL mode
  15. Execute the same query
  16. Take screenshot showing SQL results are displayed with data table
- Include success criteria:
  - Mode toggle switches between SQL and ABAP
  - ABAP mode generates ABAP code
  - SQL mode continues to work normally
  - UI clearly indicates which mode is active
  - 6+ screenshots captured

### Step 7: Update Documentation

- Read `README.md` to understand the current documentation structure
- Update the "Features" section to add a bullet point about ABAP code generation:
  - "🔧 ABAP SAP code generation for SAP system development"
- Update the "Usage" section to document the new toggle:
  - Add step explaining how to toggle between SQL and ABAP modes
  - Explain that ABAP code is generated but not executed (informational only)
  - Provide example use cases for ABAP generation
- Update the "API Endpoints" section to document the new `output_mode` parameter for `/api/query`
- Add a new section "Output Modes" that explains:
  - SQL mode: Generates and executes SQL queries against the uploaded data
  - ABAP mode: Generates ABAP code for SAP systems (informational only, no execution)

### Step 8: Run Validation Commands

- Execute all validation commands listed in the "Validation Commands" section below
- Verify all tests pass
- Verify both frontend and backend build without errors
- Verify E2E test passes and all screenshots are captured
- Fix any issues that arise and re-run validation

## Testing Strategy

### Unit Tests

- **ABAP Generation Unit Tests** (`app/server/tests/test_abap_generation.py`):
  - Test `generate_abap_with_openai()` generates valid ABAP code for simple queries
  - Test `generate_abap_with_openai()` generates valid ABAP code for complex queries
  - Test `generate_abap_with_anthropic()` generates valid ABAP code
  - Test error handling when API keys are missing
  - Test schema translation from SQL to ABAP concepts
  - Test markdown cleanup in ABAP output
  - Test routing logic in `generate_code()` function

- **Data Model Tests** (`app/server/tests/test_data_models.py`):
  - Test QueryRequest model accepts "sql" output mode
  - Test QueryRequest model accepts "abap" output mode
  - Test QueryRequest model defaults to "sql" when output mode is not specified
  - Test QueryRequest model rejects invalid output modes
  - Test QueryResponse model handles both SQL and ABAP code

- **Endpoint Tests** (`app/server/tests/test_server.py`):
  - Test `/api/query` endpoint with SQL mode returns SQL code and results
  - Test `/api/query` endpoint with ABAP mode returns ABAP code without execution
  - Test `/api/query` endpoint handles invalid output mode gracefully
  - Test backward compatibility: queries without output mode default to SQL

### Edge Cases

- User toggles between SQL and ABAP modes multiple times - verify state is maintained
- User submits query in ABAP mode with no tables uploaded - verify appropriate error message
- LLM generates ABAP code with markdown formatting - verify it's cleaned up properly
- API key is missing for selected LLM provider - verify fallback to other provider works
- User submits extremely long or complex natural language query - verify ABAP generation handles it
- Schema contains special characters or reserved ABAP keywords - verify proper escaping/handling
- Frontend loses connection during ABAP generation - verify appropriate error handling
- User switches modes while query is in progress - verify request uses the mode selected at submission time
- Browser back/forward navigation - verify mode toggle state is preserved (or resets to default)

## Acceptance Criteria

- [ ] Backend accepts `output_mode` parameter in query requests with values "sql" or "abap"
- [ ] Backend generates ABAP code when output mode is "abap" using OpenAI or Anthropic
- [ ] Backend continues to generate and execute SQL when output mode is "sql" (backward compatibility)
- [ ] Frontend displays a toggle with "SQL" and "ABAP" mode buttons that are clearly visible and accessible
- [ ] Frontend sends the selected output mode with every query request
- [ ] Frontend displays ABAP code in the results section with appropriate labeling when ABAP mode is active
- [ ] Frontend shows SQL results with data table when SQL mode is active
- [ ] Frontend indicates that ABAP code is informational only and execution is not supported
- [ ] The mode toggle persists across multiple queries within the same session
- [ ] The default mode is SQL for backward compatibility
- [ ] All existing SQL functionality continues to work without regression
- [ ] Unit tests cover ABAP generation for both OpenAI and Anthropic providers
- [ ] E2E test validates the complete ABAP generation workflow from UI toggle to code display
- [ ] Documentation is updated to explain the new ABAP conversion feature
- [ ] The UI is responsive and the toggle works on mobile devices
- [ ] Error messages are clear and helpful when ABAP generation fails

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute your new `.claude/commands/e2e/test_abap_conversion.md` E2E test file to validate the ABAP conversion functionality works end-to-end
- `cd app/server && uv run pytest tests/test_abap_generation.py -v` - Run ABAP generation unit tests
- `cd app/server && uv run pytest` - Run all server tests to validate the feature works with zero regressions
- `cd app/client && bun tsc --noEmit` - Run frontend TypeScript type checking to validate no type errors
- `cd app/client && bun run build` - Run frontend build to validate the feature builds successfully

## Notes

### ABAP Code Generation Prompt Guidance

When implementing the ABAP generation functions, use prompts that guide the LLM to generate production-quality ABAP code following SAP conventions:

- Use proper ABAP syntax: SELECT, DATA, LOOP AT, etc.
- Declare internal tables with TYPE TABLE OF
- Use proper variable naming conventions (lv* for local variables, lt* for local tables, etc.)
- Include appropriate error handling with MESSAGE statements
- Format code with proper indentation
- Add comments for complex logic
- Avoid SQL injection by using proper WHERE clause construction
- Return only the ABAP code without explanations or markdown

### Schema Translation for ABAP

The schema information will need to be translated from SQLite concepts to SAP table concepts:

- SQLite table names can be treated as custom Z tables (e.g., "users" -> "ZUSERS")
- Column types should be mapped to ABAP data types (TEXT -> CHAR, INTEGER -> INT4, etc.)
- Row count can be used to suggest performance considerations in the generated ABAP

### Future Considerations

- **ABAP Execution**: In the future, this feature could be extended to connect to an SAP system via RFC and execute the generated ABAP code remotely. This would require SAP credentials, RFC connection configuration, and proper error handling for SAP-specific exceptions.
- **ABAP Syntax Validation**: Consider adding client-side or server-side ABAP syntax validation to catch basic errors before displaying to the user.
- **ABAP Templates**: Create a library of common ABAP patterns (data retrieval, ALV reports, BAPIs) that can be used as templates for generation.
- **Multiple SAP Versions**: ABAP syntax varies across SAP versions (ECC, S/4HANA). Consider adding version selection in the future.
- **Code Export**: Add export functionality specifically for ABAP code (similar to CSV/JSON export) to save generated code to .abap files.
- **ABAP Syntax Highlighting**: Implement proper syntax highlighting for ABAP code in the frontend using a library like Prism.js or Monaco Editor.

### No New Dependencies Required

This feature can be implemented using existing dependencies:

- Backend: Uses existing OpenAI and Anthropic client libraries
- Frontend: Uses existing TypeScript and vanilla JavaScript (no new UI libraries needed)
- Testing: Uses existing pytest and Playwright frameworks
