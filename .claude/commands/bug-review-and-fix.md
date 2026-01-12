# Review Repository for Bugs

Perform a comprehensive bug review of the entire repository, identify issues, and fix them.

## Instructions

1. **Explore the Codebase**
   - List all Python files in the repository
   - Read the main source files to understand the architecture
   - Check configuration files (pyproject.toml, docker-compose.yml, etc.)

2. **Identify Bug Categories**
   Look for issues in these areas:
   - **Import errors**: Missing or incorrect imports
   - **Type errors**: Incorrect type annotations or usage
   - **Logic errors**: Flaws in conditionals, loops, or algorithms
   - **API mismatches**: Using deprecated or incorrect API signatures
   - **Configuration issues**: Missing or incorrect settings
   - **Database issues**: Schema problems, connection handling
   - **Async issues**: Missing await, incorrect async usage
   - **Error handling**: Missing try/except, incorrect error types
   - **Security issues**: SQL injection, XSS, hardcoded secrets
   - **Docker issues**: Incorrect configurations, missing dependencies

3. **Document Findings**
   For each bug found, document:
   - File and line number
   - Bug category
   - Description of the issue
   - Potential impact
   - Suggested fix

4. **Fix the Bugs**
   - Create a todo list for tracking fixes
   - Fix each bug systematically
   - Mark todos as completed after each fix
   - Verify the fix doesn't introduce new issues

5. **Report Summary**
   Provide a summary of:
   - Total bugs found
   - Bugs fixed
   - Bugs requiring user attention
   - Any recommendations for improvement

## What This Command Does

1. Scans all Python files in src/ directory
2. Analyzes code for common bug patterns
3. Uses available tools (Grep, Read, etc.) to find issues
4. Creates a todo list for tracking fixes
5. Applies fixes systematically
6. Reports findings to the user

## Example Output

```
## Bug Review Summary

### Bugs Found: 5

1. [FIXED] src/database/__init__.py:15 - Missing type hint for db instance
2. [FIXED] src/actions/notifier.py:136 - Using incorrect bot shutdown method
3. [FIXED] src/workflows/flows.py:25 - Hardcoded timestamp value
4. [INFO] config/.env.example - Missing required API key placeholders
5. [FIXED] src/models/rules.py - Missing validator for rule_type values

### Fixes Applied

- Fixed bot.shutdown() to bot.shutdown(app=Bot.DEFAULT_NONE)
- Added proper type hints for database module
- Replaced hardcoded timestamp with time.time()
- Added validator for rule_type enum values

### Recommendations

- Add unit tests for notifier module
- Consider adding pre-commit hooks for type checking
- Review database connection pooling configuration
```

## Notes

- Focus on actual bugs, not style issues
- Ask user before making breaking changes
- Preserve existing functionality when fixing bugs
- Test fixes if possible (run code, check imports)
