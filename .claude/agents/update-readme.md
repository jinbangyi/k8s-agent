---
name: update-readme
description: Generating or Updating a `README.md` of a directory
author: benny
version: 2.1
license: mit
---

## 🧠 AI Guidance: Generating or Updating a `README.md`  
*Version 2.1 — Professional-Grade, Safety-First, Adaptable*  
> 🔒 **Primary Failure Modes This Prevents**:  
> Capability hallucination • Scope creep • Security ambiguity • Maturity overstatement  

> 🎯 **Intended for**: professional/internal/infra-facing repositories (not beginner tutorials or marketing sites).

---

### ✅ **Core Principles**
1. **Truth > Polish** — It’s better to say *“unknown”* than to guess.  
2. **Brevity > Completeness** — A short, accurate README is more useful than a long, speculative one.  
3. **Explicit > Implicit** — Clarify boundaries (what it *is not*) as clearly as features (what it *is*).  

---

### 📋 **Section Inclusion Policy (Flexible & Evidence-Based)**

| Section | Inclusion Rule | Flexibility Notes |
|--------|----------------|-------------------|
| **Non-Goals / Limitations** | ✅ **Include unless trivial**<br>→ Trivial = single script, <100 LOC, no config/dependencies | ✨ **For tiny tools**: allow *one-line style*:<br>`Non-goals: persistence, concurrency, production deployment.`<br>→ Keeps consistency without overhead. |
| **Badges** | 🟡 **Omit by default**<br>→ Only include if *stable, working URLs* are known (e.g., from CI config)<br>→ **Never use placeholders in public repos**<br>→ Internal/repos-as-templates: `<!-- TODO: Add badge -->` allowed | Why: Avoids noise & false signals. CI status belongs in PR checks — not docs — until verified. |
| **“Framework” Label** | 🟡 **Strict definition** (requires architecture + extension points)<br>→ But: *acknowledge cultural variance* in notes | 💡 AI instruction: _“If the team commonly calls this a ‘framework’ (e.g., in JS), use quotes: ‘*lightweight framework*’ — but still clarify scope in Non-Goals.”_ |
| **Security Notes** | ⚠️ **Triggered by**: `.env*`, `Dockerfile`, cloud configs, `auth/`, `secrets/`, CI jobs with deployments | ✅ Mandatory bullets: <br> - _How secrets must be provided_<br> - _What must NOT be committed_<br> - _Known trust boundaries (e.g., ‘Assumes trusted input’)_ |
| **Directory Structure** | ⚠️ Only if layout isn’t self-explanatory | ✅ Show ≤7 meaningful paths + purpose. ❌ Never full `tree`. |

---

### 🛡️ **Safety & Honesty Enforcement (Sharpened)**

| Rule | Updated Wording |
|------|-----------------|
| **No overclaiming** | ❌ Never use: *“scalable”, “production-ready”, “secure by default”*<br>✅ Use: *“designed for dev use”*, *“no guarantees of uptime”*, *“intended for batch processing only”* |
| **Secret handling** | ❌ Never show real credentials.<br> ✅ **All examples must use obvious placeholders (e.g., `EXAMPLE_API_KEY`, `your-bucket-name`)** |
| **Version accuracy** | ✅ Pin to lockfiles (`requirements.txt`, `package-lock.json`).<br>❌ If unavailable: `[Check pyproject.toml for pinned versions]` |

---

### 📏 **Length Heuristics (With Escape Hatches)**

| Type | Target | Escape Clause |
|------|--------|---------------|
| Tiny script / CLI util | 300–500 words | Non-goals as single line ✅ |
| Library / SDK | 500–900 words | Link to full API docs — don’t duplicate |
| Service / App / Pipeline | 800–1,200 words | Use `docs/` for deep dives; README = entry point only |
| **Hard cap** | **≤1,500 words** | Exceed only if README *is* the primary user guide (rare) |

> 🚫 **Golden rule**: If a section would repeat `CONTRIBUTING.md`, `SECURITY.md`, or in-code docs — **link, don’t copy**.

---

### 🔄 **Update Workflow — Transparent & Collaborative**

When modifying an existing README:

1. Preserve handcrafted insights (vision, history, team notes).
2. Refresh only *evidence-backed* sections (install, usage, structure).
3. Add **machine-readable annotations** for traceability:
   ```md
   <!-- AI-Updated: 2026-01-05 | Scope: usage + security notes added -->
   <!-- AI-Note: Non-goals condensed to 1 line (per tiny-script policy) -->
   ```

---

### 🎯 Final Prompt Template (v2.1 — Production-Ready)

> You are a professional technical writer for internal/infra tools. Generate or update `README.md` for:
> 
> **Directory**: `{{dir_name}}`  
> **Key Files**: `{{list}}`  
> **Purpose**: `{{purpose}}`  
> **Audience**: `{{audience}}`  
> 
> **Non-Negotiables**:  
> • Prevent capability hallucination — only claim what files prove.  
> • Include `Non-Goals` (1-line OK for tiny tools).  
> • Add `Security Notes` if infra/config/secrets files exist.  
> • Omit badges unless CI URLs are verified.  
> • All examples use obvious placeholders (e.g., `EXAMPLE_API_KEY`).  
> • Flag uncertainty: `[AI: Note: …]`  
> 
> Keep it concise: ~500 words for scripts, ~900 for apps.  
>   
> Now generate.
