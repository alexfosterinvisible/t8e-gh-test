# E2E Test: ABAP Conversion Mode

Test the ABAP conversion feature in the Natural Language SQL Interface application.

## User Story

As a user
I want to toggle between SQL and ABAP output modes
So that I can generate ABAP code for SAP systems from natural language queries

## Test Steps

1. Navigate to the `Application URL`
2. Take a screenshot of the initial state
3. **Verify** the output mode toggle is present with "SQL" and "ABAP" buttons
4. **Verify** "SQL" mode is active by default
5. Click the "ABAP" mode button
6. Take a screenshot showing ABAP mode is active
7. Enter a natural language query like "Show me all users from the users table"
8. Take a screenshot of the query input with ABAP mode selected
9. Click the Query button
10. **Verify** ABAP code is generated and displayed (should contain ABAP syntax like "SELECT", "FROM", "INTO TABLE")
11. Take a screenshot of the ABAP code output
12. **Verify** that no results table is shown (ABAP execution not supported)
13. **Verify** a message indicates ABAP code is informational only
14. Switch back to SQL mode
15. Execute the same query
16. Take a screenshot showing SQL results are displayed with data table

## Success Criteria

- Mode toggle switches between SQL and ABAP
- ABAP mode generates ABAP code
- SQL mode continues to work normally
- UI clearly indicates which mode is active
- ABAP output contains valid ABAP syntax
- Informational message appears for ABAP mode
- 6+ screenshots captured
