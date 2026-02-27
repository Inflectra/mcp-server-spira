# Milestone 1: Fix Existing Tools

## Quick Summary

This milestone transforms existing MCP tools from markdown-based to JSON-first architecture while establishing patterns for all future tool development.

## Key Changes

### 1. JSON-First Output
- All tools return structured JSON instead of markdown
- Enables LLM filtering, sorting, and aggregation
- Preserves all data from API responses

### 2. Optional Markdown Formatting
- New dedicated formatting tools convert JSON to markdown
- Separates data retrieval from presentation
- Maintains human readability when needed

### 3. Explicit Pagination (Client-Side)
- All list tools accept `limit` and `offset` parameters
- Returns pagination metadata (total_count, has_more)
- No more silent truncation at 25 items
- **Important:** Uses client-side pagination (API returns all results, we slice in Python)
- Acceptable for "my work" endpoints (typically < 500 items)
- Future milestones will use server-side pagination for project-level queries

### 4. Comprehensive Input Validation
- Validates all parameters before API calls
- Returns structured error responses with suggestions
- Helps LLMs self-correct

### 5. Rich Tool Documentation
- Generated from OpenAPI spec
- Includes parameter details, response structure, examples
- Explains when to use each tool

### 6. Breaking Changes with Migration Path
- **Version bump:** 0.5 → 1.0 (signals breaking change)
- **Output format:** Markdown → JSON
- **Migration:** Use formatting tools for markdown output
- **Compatibility:** Tool names unchanged, clear migration guide

## Pagination Strategy

### Current Endpoints (Milestone 1)
The "my work" endpoints do NOT support server-side pagination in the Spira API:
- `GET /tasks` - Returns ALL tasks for current user
- `GET /incidents` - Returns ALL incidents for current user
- `GET /requirements` - Returns ALL requirements for current user
- `GET /test-cases` - Returns ALL test cases for current user
- `GET /test-sets` - Returns ALL test sets for current user

**Solution:** Client-side pagination
- Retrieve all results from API
- Slice in Python based on `limit` and `offset`
- Document clearly in tool descriptions
- Acceptable for typical "my work" result sets (< 500 items)

### Future Endpoints (Milestone 2+)
Project-level endpoints DO support server-side pagination:
- `GET /projects/{id}/tasks?start_row=0&number_rows=100`
- Same interface (`limit`/`offset`) but server-side implementation
- Better performance for large datasets

## Documentation Strategy

### Automated Generation
A Python script (`scripts/generate_tool_docs.py`) will:
- Parse OpenAPI spec for endpoint details
- Extract parameter and response schema information
- Generate docstring templates
- Identify areas needing human clarification

### Human Clarification
AI will ask humans when:
- OpenAPI descriptions are ambiguous or missing
- Business logic is unclear (e.g., when to use field X vs Y)
- Workflow context is needed (when to use tool A vs B)
- Data relationships are complex
- Edge cases need explanation

### Clarification Request Format
```markdown
## Clarification Request: [Tool Name]

**Context:** [Tool and endpoint info]
**Issue:** [What's unclear]
**Questions:** [Specific questions]
**Proposed Documentation:** [AI's best guess]
**Request:** [What human should review]
```

## Example Transformation

### Before
```python
def get_my_tasks() -> str:
    tasks = api.get("tasks")
    return "\n\n".join([format_task(t) for t in tasks[:25]])
```

### After
```python
def get_my_tasks(limit: int = 25, offset: int = 0) -> str:
    """
    Retrieves tasks assigned to current user.

    Args:
        limit: Max tasks to return (1-500, default: 25)
        offset: Number to skip (>= 0, default: 0)

    Returns:
        {
            "data": [...],
            "pagination": {
                "limit": 25,
                "offset": 0,
                "returned_count": 25,
                "total_count": 150,
                "has_more": true
            }
        }
    """
    # Validate inputs
    # Get data from API
    # Apply pagination
    # Return JSON with metadata
```

## Files to Review

1. **requirements.md** - Complete requirements with acceptance criteria
2. **design.md** - Technical design and implementation details (to be created)
3. **tasks.md** - Implementation task list (to be created)

## Success Criteria

- ✅ All tools return valid JSON
- ✅ All list tools support pagination
- ✅ 80%+ test coverage
- ✅ Zero silent truncations
- ✅ Clear, actionable error messages
- ✅ Documentation generated from OpenAPI spec

## Next Steps

1. Review requirements document
2. Create design document with technical details
3. Create task list for implementation
4. Begin implementation following task order
