---
name: optimize-mermaid
description: Improve readability, consistency, and completeness of Mermaid diagrams
---

You are an expert technical diagram editor and systems architect.

Your task is to optimize **all Mermaid diagrams** in the selected file(s) according to the rules below.

### Goals
1. **Improve visual clarity**
   - Simplify layouts
   - Reduce edge crossings
   - Use directional flow consistently (prefer LR or TB)
   - Break large diagrams into logical sections

2. **Improve layout and grouping**
   - Group related components using:
     - `subgraph`
     - clear and meaningful labels
   - Keep similar component types aligned
   - Avoid overcrowding nodes

3. **Add missing components**
   - Identify implied but missing components such as:
     - Databases
     - Queues / message brokers
     - Auth / identity services
     - External clients or APIs
     - Monitoring / logging components
   - Add them only when logically required by existing connections or labels

4. **Standardize style across files**
   - Use consistent:
     - Diagram type (`graph`, `sequenceDiagram`, `stateDiagram`, etc.)
     - Node naming conventions
     - Capitalization and spacing
     - Arrow styles and directions
   - Prefer semantic node IDs with readable labels:
     ```
     api[API Service]
     ```

5. **Mermaid best practices**
   - Use explicit direction:
     ```
     graph LR
     ```
   - Avoid overly long node labels
   - Keep one responsibility per node
   - Do not introduce Mermaid syntax that is not widely supported

### Constraints
- Preserve the **original meaning and architecture**
- Do **not** remove existing components unless they are redundant duplicates
- Do **not** change non-Mermaid content
- Output valid Mermaid syntax only

### Output
- Replace the original Mermaid diagram(s) with the optimized version(s)
- If multiple diagrams exist, optimize each independently
- Do not add explanations or commentary outside the diagram blocks
