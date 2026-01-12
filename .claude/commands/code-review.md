# Code Reviewer

Perform comprehensive code review including quality analysis, bug detection, and improvement suggestions.

## Instructions

1. **Discover Code to Review**
   - Check for specific files/paths provided as arguments
   - If no target specified, ask user what to review:
     - Specific file path
     - All files in a directory
     - Recently modified files (git diff)
     - Staged changes
     - Entire codebase

2. **Read and Analyze Code**
   - Read all target files
   - Understand the codebase architecture
   - Identify patterns and conventions used

3. **Perform Multi-Dimensional Review**

   **A. Correctness (Bugs & Errors)**
   - Logic errors (off-by-one, wrong conditions, etc.)
   - Type mismatches or incorrect type usage
   - Missing error handling
   - Uncaught exceptions
   - Race conditions in async code
   - Resource leaks (unclosed files/connections)
   - Incorrect API usage

   **B. Code Quality**
   - Code duplication (DRY violations)
   - Complex/nested logic (should extract functions)
   - Magic numbers/strings (should be constants)
   - Poor naming conventions
   - Overly long functions/classes
   - Inconsistent style

   **C. Security**
   - SQL injection vulnerabilities
   - XSS vulnerabilities
   - Hardcoded secrets/credentials
   - Insecure crypto usage
   - Unsafe deserialization
   - Missing input validation

   **D. Performance**
   - Inefficient algorithms (O(n²) where O(n) possible)
   - Unnecessary database queries in loops
   - Missing caching opportunities
   - Expensive operations in hot paths
   - Memory leaks (unbounded growth)

   **E. Architecture & Design**
   - Tight coupling (hard to test/change)
   - Violation of SOLID principles
   - Missing abstractions
   - God classes/functions
   - Circular dependencies

   **F. Python Best Practices**
   - Missing type hints
   - Not using context managers where appropriate
   - Reinventing stdlib functionality
   - Missing docstrings on public APIs
   - Not following PEP 8

   **G. Async/Await Issues**
   - Missing `await` on coroutines
   - Mixing sync/async incorrectly
   - Not closing async resources properly
   - Blocking event loop with sync I/O

   **H. Dependencies**
   - Unused imports
   - Missing requirements
   - Version conflicts
   - Deprecated API usage

4. **Categorize and Prioritize Findings**

   Label each issue with:
   - **Severity**: Critical / High / Medium / Low / Info
   - **Category**: (from list above)
   - **File**: `path/to/file.py:line`
   - **Title**: Brief description

5. **Create Todo List for Fixes**

   For each issue that should be fixed:
   - Add to todo list with clear action item
   - Group related fixes together
   - Order by severity

6. **Present Review Report**

   Format:
   ```
   ## Code Review Report

   ### Summary
   - Files reviewed: X
   - Issues found: Y (Z critical, A high, B medium, C low, D info)

   ### Critical Issues
   1. [path:line] Security: SQL injection vulnerability...
      - Impact: ...
      - Fix: ...

   ### High Priority
   ...

   ### Medium Priority
   ...

   ### Low Priority
   ...

   ### Positive Findings
   - Good: ...
   - Nice: ...

   ### Recommendations
   1. ...
   ```

7. **Offer to Fix Issues**

   Ask user if they want you to:
   - Fix all issues automatically
   - Fix specific issues (select which ones)
   - Generate detailed fix plans first
   - Only review, don't modify code

## What This Command Does

1. Identifies target code (files, directories, or git diff)
2. Reads and parses all target files
3. Runs static analysis looking for patterns
4. Checks for common bug patterns
5. Evaluates code quality metrics
6. Generates categorized report with severity levels
7. Creates actionable todo list
8. Optionally applies fixes with user approval

## Usage Examples

```bash
# Review specific file
/code-review src/models/rules.py

# Review entire src directory
/code-review src/

# Review staged git changes
/code-review --staged

# Review recent git diff
/code-review --diff

# Review entire codebase
/code-review
```

## Notes

- Be constructive and helpful, not overly critical
- Acknowledge good code patterns when found
- Prioritize real bugs over style nitpicks
- Ask before making breaking changes
- Explain the "why" behind suggestions
- Consider project context (new code vs legacy)
