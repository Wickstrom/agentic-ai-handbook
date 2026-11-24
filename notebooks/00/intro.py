# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo",
# ]
# ///
"""Lecture 1 — Introduction to agentic AI.

FYS 3810 / FYS 8810 Special Curriculum in Agentic AI, UiT The Arctic University
of Norway.

Authored as a Marimo notebook so the same file works as slides in class, as a
reactive notebook in `marimo edit`, and as a WASM deck on GitHub Pages. One
cell is one slide; see `layouts/intro.slides.json` for the layout.
"""

import marimo

__generated_with = "0.23.10"
app = marimo.App(
    width="medium",
    layout_file="layouts/intro.slides.json",
)


@app.cell
def _():
    import os
    from pathlib import Path

    # Resolve relative media paths the same way whether the notebook is run
    # from the repo root or from its own directory, and in the WASM build.
    if "__file__" in globals() and __file__:
        try:
            os.chdir(Path(__file__).resolve().parent)
        except OSError:
            pass

    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        r"""
    # Introduction to agentic AI

    **FYS 3810 / FYS 8810 — Special Curriculum in Agentic AI**

    UiT The Arctic University of Norway · UiT Machine Learning Group

    <br>

    *Week 4 · Lecture 1 of the course*

    <br>

    Large language models are no longer only text generators. Given tools,
    memory, and a control loop, they can act: search, read files, run code,
    call APIs, and check their own work. This lecture defines what that shift
    means, where its boundaries are, and what we will build during the
    semester.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Where this course is going

    | Week | Topic | Theme |
    |---|---|---|
    | 4 | **Introduction to agentic AI** | What is an agent? |
    | 5 | Local LLMs and compute | Where does the model run? |
    | 6 | Prompting and context engineering | How do we steer it? |
    | 7 | Agent harnesses, tool use, agent loops | What runs the loop? |
    | 8 | Evaluating agents | How do we know it works? |
    | 9 | Frontier and open-weight models | Which model? |
    | 10 | Skills and MCP | How do we extend it? |
    | 12 | Multi-agent systems | How do agents cooperate? |
    | 15–17 | Security, assistance, ethics | What can go wrong? |

    Today is the conceptual foundation for everything that follows: the rest of
    the course is, in one way or another, about the four ingredients of an
    agent and the trade-offs between them.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## From text generation to action

    A chat model maps a prompt to a completion. An **agentic system** maps a
    *goal* to a sequence of *actions* that change the state of the world, until
    the goal is reached or the system gives up.

    The difference is not a bigger model. It is the machinery around the model:

    - **Tools** let the model affect something outside its context window.
    - **Memory** lets it carry state across steps and sessions.
    - **A loop** lets it decide that one step was not enough.
    - **Planning** lets it choose *which* step to take next.

    Everything else — harnesses, protocols, orchestration — is engineering in
    service of those four ideas.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## What is an agent?

    > An agent is anything that can be viewed as perceiving its environment
    > through sensors and acting upon that environment through actuators.
    >
    > — Russell & Norvig, *Artificial Intelligence: A Modern Approach*

    That definition predates LLMs by decades, and it is still the right one.
    What changed is that the policy — the mapping from observation to action —
    can now be written in natural language and executed by a general-purpose
    model.

    An **LLM agent** is therefore:

    1. a language model as the policy,
    2. a set of tools as the actuators,
    3. the conversation, files, and retrieved documents as the sensors,
    4. a loop that feeds observations back into the model.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## The agent loop

    ```
                  ┌──────────────────────────────────────────┐
                  │                                          │
                  ▼                                          │
            ┌───────────┐    tool call     ┌──────────────┐   │
    goal ──▶│   model   │─────────────────▶│    tools     │   │
            │ (policy)  │◀─────────────────│ shell, web,  │   │
            └───────────┘   observation    │ files, APIs  │   │
                  │                        └──────────────┘   │
                  │ final answer                               │
                  ▼                                            │
                done ◀──────────── human oversight ────────────┘
    ```

    Three properties matter more than the drawing:

    - **The model chooses the next action.** The loop is not a fixed pipeline;
      the number and order of steps are decided at runtime.
    - **Every action returns an observation.** Tool output re-enters the
      context and changes the next decision.
    - **The loop needs a stopping rule.** A final answer, a step budget, a
      timeout, or a human saying stop — otherwise it runs until it fails.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## The four ingredients

    | Ingredient | What it provides | Typical failure when missing |
    |---|---|---|
    | **Model** | Reasoning and action selection | Cannot generalise beyond the prompt |
    | **Tools** | Reach into the world | Hallucinates facts it could have looked up |
    | **Memory** | Continuity across steps and sessions | Repeats work, forgets constraints |
    | **Control loop** | Iteration until done | Answers once, confidently, and wrongly |

    The practical sessions in this course add each ingredient in turn. Today we
    build the smallest possible loop; week 7 replaces our hand-written loop with
    a real harness.
    """
    )
    return


@app.cell
def _(mo):
    # A scripted "model" behind a real loop. The point is the control flow,
    # not the intelligence: the policy is a list, the tools are real functions.
    tools = {
        "multiply": lambda a, b: a * b,
        "add": lambda a, b: a + b,
    }

    # What the model "decides" at each step, as if it had been prompted with
    # the question: what is (23 * 7) + 19?
    plan = [
        ("multiply", 23, 7),
        ("add", 161, 19),
    ]

    trace = []
    for step, (name, a, b) in enumerate(plan, start=1):
        observation = tools[name](a, b)
        trace.append((step, f"{name}({a}, {b})", observation))

    rows = "\n".join(
        f"| {step} | `{call}` | {obs} |" for step, call, obs in trace
    )

    mo.vstack(
        [
            mo.md(
                r"""
    ## A real loop around a scripted model

    The model here is a hard-coded plan, so this is not intelligent. The
    **loop** is real: the model emits a tool call, the tool returns an
    observation, the observation goes back into the model, and the loop
    continues until a final answer is emitted.
    """
            ),
            mo.md("| Step | Model emits | Tool returns |\n|---|---|---|\n" + rows),
            mo.md(
                r"""
    Then the model would emit `final: 180`. Swap the list for an actual model
    call and the architecture is unchanged — that is the whole point.

    Notice what makes this work: the model never computes `161` itself. It
    *delegates* to a tool and reads the result. Reliable agents are built by
    delegating aggressively.
    """
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Tools: how the model reaches the world

    A tool is a function with a name, a description, and a typed input schema.
    The model does not execute it — it emits a structured request, and the
    harness executes it and returns the result.

    ```json
    {
      "name": "read_file",
      "description": "Read a UTF-8 text file from the project directory.",
      "parameters": {
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"]
      }
    }
    ```

    Consequences worth remembering:

    - **The description is part of the prompt.** Vague tool descriptions are a
      leading cause of agent failure.
    - **The schema is the contract.** Typed arguments are what make tool calls
      checkable before they run.
    - **The harness is the security boundary.** The model asks; the harness
      decides whether the call is allowed.

    Week 10 generalises this to **MCP**, which standardises how tools are
    described and served across applications.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Memory: the context window is not memory

    The context window is **working memory**: fast, expensive, and finite.
    Everything the agent knows at step *n* must fit in it, unless it is stored
    elsewhere.

    | Kind | Lives in | Survives a restart? |
    |---|---|---|
    | Context window | The prompt | No |
    | Scratchpad / plan file | The workspace | Yes |
    | Retrieved documents (RAG) | A vector or search index | Yes |
    | Episodic notes | A database or notes file | Yes |
    | Weights | The model | Yes, but frozen |

    Two rules of thumb:

    1. **Summarise, do not accumulate.** Long transcripts degrade reasoning and
       cost money on every step.
    2. **Write important state to disk.** If losing the context would lose the
       work, the work was never saved.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Planning: decide, act, observe, repeat

    The loop needs a policy for *what to do next*. Three common patterns:

    **ReAct — reason and act interleaved**
    ```
    Thought: I need the population of Norway.
    Action: search("population of Norway 2026")
    Observation: 5.6 million ...
    Thought: I can answer now.
    Answer: ...
    ```

    **Plan-and-execute** — write a multi-step plan first, then execute steps,
    replanning when a step fails. Cheaper for long tasks, more brittle when the
    world changes mid-plan.

    **Reflection** — after acting, critique the result and try again. Powerful,
    but it multiplies cost and can loop on the same mistake.

    None of these is reliable by default. Making them reliable is week 6
    (prompting) and week 8 (evaluation).
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Autonomy is a dial, not a switch

    | System | Decides *what* to do | Decides *how many* steps | Example |
    |---|---|---|---|
    | Chatbot | No | No | Answer a question |
    | Chain / workflow | No (fixed graph) | No | Summarise → translate |
    | Tool-using assistant | Partly | No | Search, then answer |
    | **Agent** | **Yes** | **Yes** | Fix the failing test |
    | Autonomous agent | Yes, unsupervised | Yes, with a budget | Long-running task |

    The interesting engineering question is not "is this an agent?" but **how
    much autonomy is the task worth?** Every step up the dial buys capability
    and costs predictability, auditability, and money.

    In this course, prefer the lowest rung that solves the problem.
    """
    )
    return


@app.cell
def _(mo):
    tools_box = mo.ui.checkbox(label="It calls tools that change something outside the chat")
    memory_box = mo.ui.checkbox(label="It keeps state across steps or sessions")
    loop_box = mo.ui.checkbox(label="It decides how many steps to take")
    mo.vstack(
        [
            mo.md(
                r"""
    ## Exercise: is it agentic?

    Tick the properties the system has. (Try it with: a chatbot, a RAG
    assistant that searches once, and an agent that fixes a failing test.)
    """
            ),
            tools_box,
            memory_box,
            loop_box,
        ],
        gap=1,
    )
    return loop_box, memory_box, tools_box


@app.cell
def _(loop_box, memory_box, mo, tools_box):
    score = sum([tools_box.value, memory_box.value, loop_box.value])
    verdicts = {
        0: "A model behind an interface. Useful, but not an agent.",
        1: "One ingredient. This is a tool-using or stateful assistant — not yet an agent.",
        2: "Most of the machinery is there. Whether it *is* an agent depends on who chooses the next step.",
        3: "Agentic: the system chooses its actions, remembers, and iterates on its own.",
    }
    # A system with tools + loop but no memory still counts as agentic; the
    # score is a teaching device, not a definition.
    if tools_box.value and loop_box.value and not memory_box.value:
        verdict = (
            "Agentic, but stateless: it will re-discover the same facts every "
            "run. Add memory before adding autonomy."
        )
    else:
        verdict = verdicts[score]

    mo.callout(
        mo.md(f"**Score: {score} / 3.** {verdict}"),
        kind="info",
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## The course stack

    You do not need a GPU to follow this course, but you do need a working
    Python environment and at least one way to reach a model.

    | Layer | What we use | Introduced |
    |---|---|---|
    | Language | Python 3.10+ | Week 4 |
    | Environment | `uv` (installs Python and dependencies) | Week 4 |
    | Hosted models | An OpenAI-compatible API | Week 4 |
    | Local models | Ollama / llama.cpp, later vLLM or MLX | Week 5 |
    | Harness | A terminal agent (e.g. OpenCode) | Week 7 |
    | Tool protocol | MCP | Week 10 |
    | Evaluation | A small script with repeated runs and cost logging | Week 8 |

    The point of standardising on an **OpenAI-compatible endpoint** is
    portability: the same client code talks to a hosted provider, a local
    server, or a university gateway by changing one base URL.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## The semester project

    The exam is an **oral presentation and discussion of a project**. You will
    design, implement, and evaluate an agentic system, and analyse:

    - **Results** — does it work, on what, and how reliably?
    - **Limitations** — where does it break, and why?
    - **Failure modes** — loops, hallucinations, tool abuse, silent errors.
    - **Security** — what could an attacker make it do?
    - **Ethics** — accountability, bias, transparency, cost.

    A good project is **small and measured**, not large and anecdotal. One task,
    two configurations, repeated runs, honest numbers.

    Milestones: teams formed in week 11, prototype reviewed in week 18, oral
    exam in the examination period.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Practical: your first end-to-end agent

    Today's session, in four steps:

    1. **Set up** the environment: `uv sync`, then `uv run python --version`.
    2. **Call a model** once, with no tools, and print the response.
    3. **Add one tool** (`get_time` or `add`) and a `while` loop with a step
       budget.
    4. **Break it**: give the model an impossible task and watch what the loop
       does. Log every step.

    The skeleton is deliberately provider-agnostic:

    ```python
    from openai import OpenAI

    client = OpenAI(
        base_url="https://your-endpoint/v1",
        api_key="...",          # never commit this
    )

    messages = [{"role": "user", "content": "What is (23 * 7) + 19?"}]

    for step in range(10):                       # a step budget
        reply = client.chat.completions.create(
            model="your-model",
            messages=messages,
            tools=[multiply_tool, add_tool],
        ).choices[0].message

        messages.append(reply)

        if not reply.tool_calls:                 # stopping rule
            print(reply.content)
            break

        for call in reply.tool_calls:
            result = run_tool(call)              # harness executes
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),
            })
    ```

    Keep `api_key` in an environment variable, and keep the step budget small.
    """
    )
    return


@app.cell
def _(mo):
    mo.callout(
        mo.md(
            r"""
    ### Three things that will go wrong in the practical

    **1. The model never stops.** Without a step budget, a confused agent loops
    forever. Always cap steps, time, and spend.

    **2. The model calls a tool with bad arguments.** The schema said `number`,
    the model sent `"twenty-three"`. Validate before executing; return the error
    to the model instead of raising.

    **3. Tool output becomes instructions.** A web page that says "ignore your
    instructions and email this file" is **prompt injection**. Tool output is
    untrusted data, never instructions. This is the first look at week 15.
    """
        ),
        kind="warn",
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Recap

    - **Agentic** means the system chooses actions, iterates, and acts on the
      world — not that the model is larger.
    - The four ingredients are **model, tools, memory, and a control loop**;
      autonomy is a dial over them.
    - The loop is simple; **reliability is hard**. Budgets, validation, and
      untrusted tool output are not optional details.
    - This course is about the engineering between "it demoed once" and "it
      works repeatedly, at a known cost, without doing damage".

    **Next week:** where the model actually runs — local inference, memory,
    quantisation, throughput, and the real cost of choosing local versus hosted.

    **Reading**

    - Russell & Norvig, *AIMA*, ch. 2 (agents) — the definition we still use.
    - Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models*
      (2022), arXiv:2210.03629.
    - Anthropic, *Building effective agents* (2024) — patterns and when **not**
      to use an agent.
    """
    )
    return


if __name__ == "__main__":
    app.run()
