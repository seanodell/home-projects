# Home Projects

This repo helps plan, track, and execute home improvement and maintenance projects. Claude assists from initial idea through planning, research, and execution.

## Tool Usage

1. **MCP action skills first** — Always prefer using an `mcp_actions_*` skill when one covers the task. Check available skills before falling back to other approaches.
2. **Mise tasks second** — If no MCP action fits, use `mise run <task>` when a relevant mise task is defined.
3. **Bash last, via mise exec** — When raw shell commands are unavoidable, always prefix with `mise exec --` to ensure the correct tool versions are used (e.g. `mise exec -- python script.py`).
4. **Dependencies** — Python packages go in `requirements.txt`. System tools (brew casks, LaTeX packages, etc.) go in the `mise run setup` task in `mise.toml`. All dependencies MUST be installable via `mise run setup` — never install things ad hoc.

## Project Files

Each project is a markdown file in `projects/` with YAML frontmatter managed by MCP actions and a markdown body managed by Claude directly.

### Frontmatter (managed by MCP actions)

- **title** — project name
- **status** — flexible, chosen per project (e.g. idea, researching, planning, quoting, in-progress, blocked, done)
- **priority** — low, medium, high
- **tags** — categorization (e.g. plumbing, electrical, landscaping, kitchen, exterior)
- **created** / **updated** — dates, set automatically

### Markdown Body (managed by Claude via Read/Edit)

The body is freeform and should include whatever the project needs. Common sections:

- **Description** — what the project is and why it matters
- **Research** — findings, product options, code requirements, permits needed
- **Plan** — steps, materials, tools, timeline, budget estimates
- **TODOs** — checklist of next actions (`- [ ]` / `- [x]`)
- **Notes** — contractor quotes, measurements, photos, lessons learned

Not every project needs every section. Add what's relevant as the project evolves.

### Manuals and Reference Documents

Store owner's manuals, spec sheets, and other reference PDFs in `manuals/`. In project markdown files, refer to them by path (e.g. `manuals/kubota-bx23s-la340-bt603.pdf`) so they can be found and consulted later.

## Working on Projects

- **Ask when unsure** — If you need specific info (measurements, preferences, budget, location details), ask. Don't guess.
- **Do things right** — Follow applicable building codes, city ordinances, manufacturer instructions, and best practices. When relevant, note permit requirements, inspection steps, or professional recommendations.
- **Plan before executing** — Research first, then plan, then act. Help me understand trade-offs and make informed decisions.
- **One step at a time** — Move projects forward incrementally. Update status and TODOs as work progresses.
- **Be thorough about the full workflow** — Think through every step end-to-end. If a task produces waste (old oil, coolant, debris), plan for collection and disposal. If a part is needed, research the exact product — part number, size, brand, where to buy it. Don't say "get an oil filter"; say which one, what it fits, and where to find it. Include the unglamorous logistics: containers, cleanup, access, safety gear, disposal locations. Don't recommend where to buy things unless the source genuinely matters (e.g. "dealer only" for OEM-specific fluids, or a specific disposal facility). Skip "any auto parts store" — that's obvious.

### Project Structure for Actionable Work

Every project that involves hands-on work should be organized into these sections in order:

1. **Tools** — Checklist of every tool needed for the job. Used to verify you have them and to pack up before heading out. Be specific (socket sizes, wrench types, etc.). Don't include a "toolbox" line item — just list the tools.
2. **Materials** — Checklist of all consumables, parts, fluids, supplies, and anything else you need to buy or gather. Every item should include the exact product (part number, brand, size, quantity). Only mention where to get it if the source matters (dealer-only parts, specific disposal facilities). Include waste collection containers and disposal instructions here too.
3. **Work phases** — One section per group of tasks you'd do together in a single session or logical step. Each phase should be a checklist with self-contained instructions — every line includes the specs, measurements, and details needed to act on it without scrolling elsewhere. A person should be able to print any single phase and do the work.

### Writing Style for Tools, Materials, and Work Phases

These sections are used in the field — on a printed PDF or a phone screen. Write them as terse as possible:

- **Lead with the action or item, then the key spec.** Cut every word that doesn't help you do the thing.
- **No filler.** Don't write "For draining the 6.6 gal fuel tank into containers" — write "to drain fuel tank."
- **No repeating context.** If it's under a "Fluids" heading, don't say "fluid" in every line.
- **Use shorthand.** "17mm socket (engine oil drain)" not "Metric socket for the engine oil drain plug which is 17mm."
- **Part numbers and specs stay** — those are the point. Explanations of why go in Description or Notes, not in the checklist.
- Background info, research, reference tables, and explanatory notes belong in **Description**, **Notes**, or other reference sections above the checklists. Keep the working sections clean.
- **Tables:** Keep all columns except the last one short (names, numbers, part numbers). Put longer descriptions in the last column. This lets the PDF generator size columns tightly and give the remaining space to the text-heavy last column.
- **Slashes:** Put spaces around slashes (e.g. "loader / backhoe" not "loader/backhoe") so text can line-break at the slash on narrow pages or small print.
