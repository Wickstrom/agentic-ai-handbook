# Contributing

This repository holds the lecture decks for **FYS 3810 / FYS 8810 — Special
Curriculum in Agentic AI**. It is course material, not a software library, but
the same rules apply: small changes, reviewable diffs, and no secrets.

## Adding or editing a lecture

1. Copy the closest existing lecture in `notebooks/` as a template. Each one
   starts with PEP 723 metadata, creates `marimo.App(..., layout_file=...)`,
   and uses one `@app.cell` per slide.
2. Create the layout file next to it:
   `notebooks/<nn>/layouts/<name>.slides.json` containing
   `{"type": "slides", "data": {}}`. Marimo rewrites it when you arrange the
   slides in `marimo edit`.
3. Register the lecture in **both** places:
   - the **Content** section of `README.md`,
   - the module list in `index.html`.
4. Export and check before committing:

   ```bash
   ./scripts/build_slides.sh
   python3 -m http.server -d _slides 8000
   ```

## Writing conventions

- **One idea per slide.** If it needs scrolling, split it.
- **Markdown first.** Interactivity is for quantities that are hard to grasp
  statically (memory, cost, tokens per second) — not decoration.
- **WASM-compatible.** Anything exported to the site must run in the browser:
  pure Python plus `marimo`. Avoid native extensions and large downloads.
- **No secrets.** Read API keys from environment variables; never paste them
  into a cell, an output, or a commit.
- **Cite.** Papers, documentation, and model versions go on the recap slide.
  The field changes quickly; an uncited claim ages badly.
- **Be explicit about uncertainty.** Numbers in slides are estimates; say what
  they assume (quantisation, bandwidth, utilisation).

## Commits

Keep the subject line in the imperative mood (`Add lecture on evaluating
agents`) and mention the lecture directory in the body when the change is
localised.
