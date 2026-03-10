# Learnings Directory Guide

This directory tracks lessons learned during development. When you discover something non-obvious that took debugging to figure out, document it here.

## Quick Start for New Agents

1.**Read the index first:** `af-learnings-index.md` — this is your cheatsheet
→ NB: Exemplar with real content: `~/.claude/af-templates/.learnings/af-learnings-index-exemplar.md` 2.**Read one example:**`L000-EXAMPLE-sandbox-fs-write-tool.md` shows the full format (content irrelevant)
→ NB: if this example isn't present, cp from `~/.claude/af-templates/.learnings/L000-EXAMPLE-sandbox-fs-write-tool.md` 3.**Check before documenting:** Search index to avoid duplicates

## Setup

cp -r ~/.claude/af-templates/.learnings/\* ./.learnings/

## When to Add a Learning

Add a learning when:

- You spent significant time debugging something
- The root cause wasn't obvious from error messages
- Future agents would hit the same issue
- You verified both the cause AND the fix

Do NOT add:

- Trivial fixes (typos, missing imports)
- Unverified theories
- Generic programming knowledge

## File Format

### Index Entry (`af-learnings-index.md`)

```markdown
## L00X: Short Descriptive Title

**Problem:** One-line description of what went wrong
**Cause:** One-line root cause
**Verified cause:** How you confirmed the cause (grep, source read, etc.)
**Fix:** One-line solution
**Verified fix:** How you confirmed it works
**Detail:** [L00X-slug.md](./L00X-slug.md)
```

Note: Left-align content after colons for readability in IDE.

### Detailed File (`L00X-slug.md`)

```markdown
# L00X: Short Descriptive Title

## Summary

One paragraph explaining the issue and its importance.

## Discovery

How you encountered the problem. Include error messages.

## Root Cause

Technical explanation with code snippets if relevant.

## Solution

The fix, with code examples.

## Result

- Before: [what happened]

- After: [what happens now]

## Verification (Cause)

**Method:** How you confirmed the root cause

**Command:** Actual command you ran

**Result:** What you found

**Confirmed:** What this proves

## Verification (Fix)

**Method:** How you tested the fix

**Before fix:** Command and output

**After fix:** Command and output

## Files Changed

- List of files modified

## Implications (optional)

Broader impact or future considerations.
```

## Numbering

- Use `L001`, `L002`, etc.
- Check existing numbers before adding
- Don't reuse numbers even if a learning is deleted

## Naming Conventions

- Index: `af-learnings-index.md`
- Details: `L00X-short-slug.md` (lowercase, hyphens)
- This guide: `CLAUDE.md`

## Example Workflow

```

1. Hit weird error

2. Debug and find root cause

3. Verify cause by reading source/grepping

4. Implement fix

5. Verify fix works (run tests, scenario, etc.)

6. Document in index + detailed file

7. Commit with message: "docs: Add learning L00X - short description"

```


## Diagram Fidelity

- ASCII diagrams must always be included verbatim exactly as originally written when included in the full `.md`.
