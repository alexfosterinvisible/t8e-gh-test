# Patch: Create Missing E2E Test File for ABAP Conversion

## Metadata

adw_id: `6b5c2c81`
review_change_request: `Issue #1: E2E test file missing: The spec explicitly requires creating .claude/commands/e2e/test_abap_conversion.md in Step 6 with detailed test steps for validating the ABAP conversion feature end-to-end. This file does not exist in the implementation. Resolution: Create the E2E test file .claude/commands/e2e/test_abap_conversion.md following the format specified in Step 6 of the spec, including all 16 test steps and success criteria for validating mode toggle, ABAP code generation, and SQL/ABAP mode switching. Severity: blocker`

## Issue Summary

**Original Spec:** specs/issue-13-adw-6b5c2c81-sdlc_planner-nlp-to-abap-conversion.md
**Issue:** Step 6 of the spec requires creating `.claude/commands/e2e/test_abap_conversion.md` with 16 detailed test steps to validate the ABAP conversion feature end-to-end. This file was not created during implementation, making it impossible to validate the feature works correctly.
**Solution:** Create the E2E test file following the exact format and structure specified in Step 6 of the original spec, including all 16 test steps, success criteria, user story, and screenshot requirements.

## Files to Modify

Use these files to implement the patch:

- `.claude/commands/e2e/test_abap_conversion.md` - Create new E2E test file (does not exist yet)

## Implementation Steps

IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test File Structure

- Create `.claude/commands/e2e/test_abap_conversion.md` with the standard E2E test format
- Add user story section describing the ABAP conversion feature from the user's perspective
- Structure the file to match the format used in `.claude/commands/e2e/test_basic_query.md`

### Step 2: Add All 16 Test Steps

- Add test step 1: Navigate to the application URL
- Add test step 2: Take screenshot of initial state
- Add test step 3: **Verify** the output mode toggle is present with "SQL" and "ABAP" buttons
- Add test step 4: **Verify** "SQL" mode is active by default
- Add test step 5: Click the "ABAP" mode button
- Add test step 6: Take screenshot showing ABAP mode is active
- Add test step 7: Enter a natural language query like "Show me all users from the users table"
- Add test step 8: Take screenshot of the query input with ABAP mode selected
- Add test step 9: Click the Query button
- Add test step 10: **Verify** ABAP code is generated and displayed (should contain ABAP syntax like "SELECT", "FROM", "INTO TABLE")
- Add test step 11: Take screenshot of the ABAP code output
- Add test step 12: **Verify** that no results table is shown (ABAP execution not supported)
- Add test step 13: **Verify** a message indicates ABAP code is informational only
- Add test step 14: Switch back to SQL mode
- Add test step 15: Execute the same query
- Add test step 16: Take screenshot showing SQL results are displayed with data table

### Step 3: Add Success Criteria

- Add success criteria: Mode toggle switches between SQL and ABAP
- Add success criteria: ABAP mode generates ABAP code
- Add success criteria: SQL mode continues to work normally
- Add success criteria: UI clearly indicates which mode is active
- Add success criteria: 6+ screenshots captured
- Format all success criteria as a bulleted list for easy validation

## Validation

Execute every command to validate the patch is complete with zero regressions.

- `cat .claude/commands/e2e/test_abap_conversion.md` - Verify the file exists and contains all required sections
- `grep -c "^[0-9]\\+\\." .claude/commands/e2e/test_abap_conversion.md` - Verify 16 test steps are present
- `grep -c "\\*\\*Verify\\*\\*" .claude/commands/e2e/test_abap_conversion.md` - Verify verification steps are included
- `grep "User Story" .claude/commands/e2e/test_abap_conversion.md` - Verify user story section exists
- `grep "Success Criteria" .claude/commands/e2e/test_abap_conversion.md` - Verify success criteria section exists

## Patch Scope

**Lines of code to change:** ~70 lines (new file creation)
**Risk level:** low
**Testing required:** Manual verification that file exists and contains all required sections as specified in Step 6 of the original spec
