## Rules

### 📌 Mermaid Diagram Rules

**1. Syntax Case Sensitivity**
- All Mermaid keywords are case-sensitive
- Always use lowercase keywords (e.g. `graph`, `subgraph`, `classDef`)
- Incorrect casing (e.g. `Graph` or `ClassDef`) causes parsing errors

**2. Valid Node Labels**
- HTML tags like `<br/>` are generally valid for line breaks in labels (especially in sequenceDiagram and flowchart)
- However, for labels with special characters like parentheses `()`, slashes `/`, or other operators, use double quotes
- Example: `Node["Label with (parentheses) and /slashes"]` instead of `Node[Label with (parentheses) and /slashes]`
- Keep labels simple and descriptive
- Use parentheses or separate nodes for additional information

**3. Diagram Structure**
- For complex architectures with nested subgraphs, use `graph TD` (top-down) layout for readability
- Use clear, consistent node naming with hyphen separators (e.g. `dmz-subnet` instead of `dmzSubnet`)
- Group related nodes within subgraphs for logical organization

**4. Styling Guidelines**
- Use `classDef` to define reusable styles
- Keep class names simple and descriptive
- Use consistent color schemes for similar resource types

**5. Validation**
- Always validate diagrams using `mmdc` (Mermaid CLI)
- Example command: `mmdc -t neutral -i diagram.mmd -o diagram.svg`
- Fix any parsing errors before committing
