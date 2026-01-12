# Guidance for Claude Code Slash Command: `update-root-docs`

## Purpose

The `update-root-docs` slash command is designed for **Claude Code (CLI agent)** to keep **root-level documentation** accurate, current, and aligned with the actual codebase and repository structure.

This command ensures that high-signal documents such as `README.md` and `CLAUDE.md` remain trustworthy sources of truth for both humans and autonomous agents.

---

## Scope

The agent must operate **only on root documentation files**:

* `README.md`
* `CLAUDE.md`

The agent must not modify source code, configuration files, or non-root documentation unless explicitly instructed.

---

## Inputs & Outputs

### Inputs

* Current repository state (filesystem, detected tooling, existing root docs)

### Outputs

* Updated `README.md` and/or `CLAUDE.md`
* No other files modified
* Changes must be reviewable via a minimal, focused diff

---

## When to Use

Trigger `update-root-docs` when:

* Project structure changes (directories, tooling, languages)
* Build, run, or deploy instructions change
* AI usage rules or contribution workflows evolve
* New major features or responsibilities are added
* Existing root documentation becomes outdated or misleading

---

## Command Intent (High-Level)

When invoked, the agent must:

1. **Analyze the repository**

   * Inspect directory structure
   * Detect explicit signals, including:

     * `package.json` → Node.js
     * `pyproject.toml`, `requirements.txt` → Python
     * `go.mod` → Go
     * `Dockerfile`, `docker-compose.yml`
     * `.github/workflows/*` → CI hints
   * Prefer observed files and commands over inferred behavior

2. **Evaluate documentation accuracy**

   * Compare existing docs against the actual repository state
   * Identify missing, outdated, or incorrect sections

3. **Update documentation conservatively**

   * Preserve existing intent and tone
   * Improve clarity and correctness only where verifiable
   * Avoid speculative or unverifiable claims

4. **Produce clean, minimal diffs**

   * Edit only what is necessary
   * Do not reformat or restructure without clear justification

---

## README.md Update Rules

### Purpose

`README.md` is written for **human readers**, especially new contributors.

### Required Sections (If Applicable)

Required sections must only be added if the information can be **directly verified** from the repository.

If verification is incomplete, the agent must add a clearly marked TODO rather than a guessed instruction.

Typical sections include:

* Project purpose (1–2 concise paragraphs)
* Key features or responsibilities
* Tech stack (languages, frameworks, major dependencies)
* How to run locally
* How to build and test (if applicable)
* How to deploy (if applicable)

### Style Guidelines

* Clear and concise
* Optimized for onboarding
* Prefer bullet points over long prose
* Avoid marketing language

### Prohibited Actions

* Do not invent features
* Do not reference tools not present in the repository
* Do not remove valuable context without replacement

---

## CLAUDE.md Update Rules

### Purpose

`CLAUDE.md` defines **how the agent must work with this repository**.

It is the authoritative contract between the repository and Claude Code.

### Content Expectations

`CLAUDE.md` must include:

* Repository overview from an agent’s perspective
* Coding standards and conventions
* Project structure explanation
* Testing expectations
* Safe areas vs sensitive areas
* Rules governing how the agent may make changes

### Tone and Structure

* Written as **imperative instructions**, not narrative descriptions
* Direct, unambiguous, and operational
* Optimized for autonomous CLI execution

---

## Safety & Correctness Rules

The agent must:

* Never guess undocumented behavior
* Never delete instructions without justification
* Prefer TODO notes over assumptions
* Preserve existing constraints unless clearly obsolete
* Not introduce new sections unless there is clear evidence they are needed

If uncertainty exists, the agent must:

* Leave the section unchanged, or
* Add a clearly marked TODO or NOTE

---

## Creation vs Update Priority

Updating existing documentation always takes precedence over creating new content.

---

## Missing or Empty Documentation

* If a required root document does not exist, the agent may create it only with:

  * Clearly scoped, minimal content
  * Explicit TODOs where information cannot be verified

---

## Failure Modes

If the agent cannot confidently determine how the project is built, run, or tested, it must:

* Leave the relevant section unchanged, or
* Add a TODO explaining what could not be verified

---

## Non-Goals

This command is not responsible for:

* Refactoring code
* Updating version numbers
* Generating changelogs
* Modifying non-root documentation

---

## Success Criteria

The command is successful if:

* A new contributor can run the project using `README.md` alone
* The agent can safely operate using only `CLAUDE.md`
* Documentation matches repository reality with no obvious contradictions

---

## Summary

`update-root-docs` is a **documentation alignment command**.

Its sole responsibility is to keep root-level documentation:

* Accurate
* Minimal
* Actionable
* Safe for autonomous agent use

Nothing more. Nothing less.
