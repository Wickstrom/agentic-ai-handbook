# Agentic AI

Material for the course **FYS 3810 / FYS 8810 — Special Curriculum in Agentic AI**
at UiT The Arctic University of Norway.

Agentic AI is the engineering of systems in which large language models are given
tools, memory, and the ability to plan and act over multiple steps. The course
combines short presentations with hands-on sessions, and is examined through a
project where students design, implement, and evaluate an agentic system and
analyse its results, limitations, failure modes, and ethical and security
implications.

This repository holds the lecture notebooks. They are written as
[Marimo](https://marimo.io) notebooks: the same file is the source, the live
notebook, the slide deck, and the browser-runnable WebAssembly app.

> **Status:** draft. The first two lectures are drafted here; the rest of the
> syllabus is being written as the course runs. See [Roadmap](#-roadmap).

## 📑 Content

### Module 1 — Foundations

1. **Introduction to agentic AI** *(week 4)*
   - From text generation to action
   - What makes a system agentic: tools, memory, planning, autonomy
   - The agent loop, and a minimal end-to-end agent
   - Course stack, semester project, first look at prompt injection

   [![Slides](https://img.shields.io/badge/-Slides-blue?logo=marimo&style=flat&labelColor=gray)](notebooks/00/intro/index.html)
   · [source](notebooks/00/intro.py)

### Module 2 — Running models

2. **Local LLMs and compute** *(week 5)*
   - Weights, precision, and the KV cache
   - Quantisation and inference engines (Ollama, llama.cpp, vLLM, MLX)
   - Memory bandwidth, tokens per second, batching, and latency
   - Local versus hosted: cost, capability, privacy

   [![Slides](https://img.shields.io/badge/-Slides-blue?logo=marimo&style=flat&labelColor=gray)](notebooks/01/local_llms/index.html)
   · [source](notebooks/01/local_llms.py)

The slide links are relative to the published site (see
[Building the decks](#-building-the-decks)); on GitHub they point at paths that
only exist after a build.

## 🗂 Repository layout

```
notebooks/
├── 00/intro.py                 # Lecture 1 — Introduction to agentic AI
│   └── layouts/intro.slides.json
└── 01/local_llms.py            # Lecture 2 — Local LLMs and compute
    └── layouts/local_llms.slides.json
index.html                      # Landing page for the published site
scripts/build_slides.sh         # Export every deck to _slides/ locally
.github/workflows/publish-slides.yml
pyproject.toml                  # Python and dependency pinning for `uv`
```

Each lecture is **one cell per slide**. Slide order and any hidden cells are
stored in the sibling `layouts/*.slides.json`, which Marimo writes when you
edit the layout in `marimo edit` (the *slides* layout panel).

## 💻 How to run locally

The repo is packaged with [uv](https://docs.astral.sh/uv/), which installs
Python and the dependencies in one step:

```bash
uv sync
uv run marimo edit notebooks/00/intro.py
```

Each notebook also carries PEP 723 inline metadata, so `uv run marimo edit
notebooks/00/intro.py` works without `uv sync` first. Editing a deck opens the
reactive notebook; switch to the slide layout from Marimo's layout menu to
present it.

To present without editing:

```bash
uv run marimo run notebooks/00/intro.py
```

## 🎞 Building the decks

`scripts/build_slides.sh` exports every notebook to a standalone WebAssembly
page under `_slides/`, together with the landing page:

```bash
./scripts/build_slides.sh
python3 -m http.server -d _slides 8000   # then open http://localhost:8000
```

The GitHub Actions workflow runs the same export on every push to `main` and
deploys `_slides/` to GitHub Pages.

> **Note on publishing.** Both this repository and the Pages site are public.
> Never commit API keys or student data: the practical code reads credentials
> from environment variables. Use the local build
> (`./scripts/build_slides.sh`) if you want to preview a draft without
> publishing it.

## ✍️ Adding a lecture

1. Create `notebooks/<nn>/<name>.py` using an existing lecture as the template
   (header, `marimo.App`, one `@app.cell` per slide).
2. Add `notebooks/<nn>/layouts/<name>.slides.json` containing
   `{"type": "slides", "data": {}}`, then arrange slides in `marimo edit`.
3. Add the lecture to the README **Content** section and to `index.html`.
4. Run `./scripts/build_slides.sh` and check the export before committing.

Conventions:

- **One idea per slide.** If a slide needs scrolling, split it.
- **Slides are markdown-first.** Interactive calculators are welcome where
  they teach a quantity (memory, cost, tokens/s); they must run in WASM, so
  use pure Python plus `marimo`, not native extensions.
- **No secrets in notebooks.** Practical code reads keys from environment
  variables.
- **Cite claims.** Papers, documentation, and versions belong in the recap
  slide; the field moves too fast for uncited assertions.

## 🗺 Roadmap

| Week | Topic | Status |
|---|---|---|
| 4 | Introduction to agentic AI | ✅ |
| 5 | Local LLMs and compute | ✅ |
| 6 | Prompting and context engineering | planned |
| 7 | Agent harnesses, tool use, and agent loops | planned |
| 8 | Evaluating agents | planned |
| 9 | Frontier and open-weight models | planned |
| 10 | Skills and the Model Context Protocol (MCP) | planned |
| 11 | Forming teams and planning projects | — |
| 12 | Multi-agent systems and orchestration | planned |
| 15 | Cyber security | planned |
| 16 | Personal assistance | planned |
| 17 | Ethics and responsible use | planned |

## 🙏 Acknowledgements

The structure of this repository — Marimo decks, WASM export, and a
`uv`-packaged Python environment — follows the
[Pattern Recognition handbook](https://github.com/Wickstrom/pattern-recognition-handbook)
and, upstream of it, [Time Series Analysis with Python](https://github.com/FilippoMB/python-time-series-handbook).
