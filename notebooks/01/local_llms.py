# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo",
# ]
# ///
"""Lecture 2 — Local LLMs and compute.

FYS 3810 / FYS 8810 Special Curriculum in Agentic AI, UiT The Arctic University
of Norway.

Covers what it means to run a model yourself: weights and precision, KV-cache
memory, quantisation, inference engines, the memory-bandwidth limit on tokens
per second, batching, and the cost trade-off against hosted APIs.
"""

import marimo

__generated_with = "0.23.10"
app = marimo.App(
    width="medium",
    layout_file="layouts/local_llms.slides.json",
)


@app.cell
def _():
    import os
    from pathlib import Path

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
    # Local LLMs and compute

    **FYS 3810 / FYS 8810 — Special Curriculum in Agentic AI**

    UiT The Arctic University of Norway · UiT Machine Learning Group

    <br>

    *Week 5 · Lecture 2 of the course*

    <br>

    Last week the model was a service we called. This week it is a file on
    disk, a number of bytes in memory, and a rate of tokens per second that we
    can predict before spending a cent.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Why run a model yourself?

    | Concern | Hosted API | Local model |
    |---|---|---|
    | Capability | Frontier models | Usually one generation behind, sometimes close |
    | Privacy | Prompts leave the machine | Data stays local |
    | Marginal cost | Per token, forever | Electricity + hardware |
    | Latency | Network + queue | No network, but slower decode |
    | Availability | Needs connectivity | Works offline |
    | Control | Provider decides versions and limits | You pin the weights |
    | Operations | None | You own the stack |

    Three honest reasons to go local:

    1. **Confidential data** that cannot leave the institution.
    2. **High, steady volume** where the API bill exceeds hardware.
    3. **Reproducibility** — a pinned set of weights does not change under you.

    One honest reason not to: *"local is cheaper"* is false at low volume once
    you count your own time.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## What "running a model" actually means

    A model is a stack of matrix multiplications. Three numbers decide whether
    it fits on your machine:

    - **Parameters** — how many weights, in billions (8B, 70B).
    - **Precision** — how many bits per weight (FP16 = 16, Q4 ≈ 4.5).
    - **Context** — how many tokens of history are live at once.

    Weights are the easy part:

    ```
    weights (GB) ≈ parameters (B) × bits per weight / 8
    ```

    An 8B model at FP16 is ~16 GB; at 4-bit it is ~4.5 GB. The **KV cache** —
    the attention keys and values for every live token — grows with context and
    is often what actually runs you out of memory.
    """
    )
    return


@app.cell
def _(mo):
    model_specs = {
        "Llama 3.1 8B": {"params_b": 8.0, "layers": 32, "kv_heads": 8, "head_dim": 128},
        "Qwen2.5 7B": {"params_b": 7.6, "layers": 28, "kv_heads": 4, "head_dim": 128},
        "Mistral 7B": {"params_b": 7.2, "layers": 32, "kv_heads": 8, "head_dim": 128},
        "Llama 3.3 70B": {"params_b": 70.6, "layers": 80, "kv_heads": 8, "head_dim": 128},
    }

    model_pick = mo.ui.dropdown(
        options=list(model_specs),
        value="Llama 3.1 8B",
        label="Model",
    )
    weight_bits = mo.ui.slider(
        start=2, stop=16, step=1, value=4, label="Weight precision (bits)"
    )
    kv_bits = mo.ui.dropdown(
        options={"FP16 (2 bytes)": 16, "FP8 (1 byte)": 8},
        value="FP16 (2 bytes)",
        label="KV-cache precision",
    )
    context = mo.ui.slider(
        start=1024, stop=131072, step=1024, value=8192, label="Context length (tokens)"
    )
    mo.vstack(
        [
            mo.md(
                r"""
    ## Calculator: will it fit?

    Move the sliders. Total memory uses a 10 % runtime overhead for the
    inference engine, activations, and fragmentation — a rule of thumb, not a
    guarantee.
    """
            ),
            mo.hstack([model_pick, kv_bits], justify="start", gap=2),
            weight_bits,
            context,
        ],
        gap=1,
    )
    return context, kv_bits, model_pick, model_specs, weight_bits


@app.cell
def _(context, kv_bits, model_pick, model_specs, mo, weight_bits):
    spec = model_specs[model_pick.value]

    weights_gb = spec["params_b"] * weight_bits.value / 8
    kv_bytes = kv_bits.value / 8
    kv_gb = (
        2
        * spec["layers"]
        * spec["kv_heads"]
        * spec["head_dim"]
        * context.value
        * kv_bytes
    ) / 1e9
    total_gb = (weights_gb + kv_gb) * 1.10

    fit = (
        "Fits on a 16 GB laptop with room to spare."
        if total_gb <= 12
        else "Fits on a 24 GB GPU, tight on a 16 GB machine."
        if total_gb <= 24
        else "Needs a 48 GB GPU, a 64 GB+ unified-memory machine, or a smaller quantisation."
        if total_gb <= 48
        else "Multi-GPU or aggressive quantisation; check the hardware before committing."
    )

    mo.vstack(
        [
            mo.hstack(
                [
                    mo.stat(value=f"{weights_gb:.1f} GB", label="Weights"),
                    mo.stat(value=f"{kv_gb:.2f} GB", label="KV cache"),
                    mo.stat(value=f"{total_gb:.1f} GB", label="Total (+10 %)"),
                ],
                justify="start",
                gap=2,
            ),
            mo.callout(mo.md(f"**{fit}**"), kind="info"),
            mo.md(
                r"""
    Try 70B at 16 bits and watch the weights alone pass 140 GB. Then switch to
    4 bits: the weights shrink 4×, but at a 128k context the KV cache becomes
    the larger term. That is why **long context is a memory decision**, not
    just a prompt decision.
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
    ## Quantisation: trading precision for memory

    Quantisation stores weights with fewer bits. The model does not get
    smaller in parameters, only in bytes.

    | Format | Bits/weight (approx.) | 8B model | 70B model | Typical quality |
    |---|---|---|---|---|
    | FP16 / BF16 | 16 | 16 GB | 141 GB | Reference |
    | FP8 | 8 | 8 GB | 71 GB | Near-lossless |
    | Q8_0 | 8.5 | 8.5 GB | 75 GB | Near-lossless |
    | **Q5_K_M** | ~5.7 | 5.7 GB | 48 GB | Very small loss |
    | **Q4_K_M** | ~4.8 | 4.8 GB | 40 GB | Good default |
    | Q3_K_M | ~3.9 | 3.9 GB | 33 GB | Noticeable degradation |
    | Q2_K | ~3.4 | 3.4 GB | 29 GB | Degraded; last resort |

    Practical notes:

    - **4–5 bits is the sweet spot** for local work. Below 4 bits, instruction
      following and tool calling degrade faster than benchmarks suggest.
    - **Agentic use punishes quantisation.** A model that is 2 % worse on
      multiple-choice can be much worse at emitting valid tool-call JSON.
    - Always **evaluate the quantised model on your own task**; published
      perplexity numbers do not transfer reliably.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Inference engines

    The weights are the same; the engine decides how efficiently they are
    executed.

    | Engine | Formats | Best for | Notes |
    |---|---|---|---|
    | **Ollama** | GGUF | Laptops, quick start | Wraps llama.cpp, manages models, OpenAI-compatible API |
    | **llama.cpp** | GGUF | CPU, Apple Silicon, edge | Maximum control, quantisation built in |
    | **vLLM** | HF safetensors, AWQ, GPTQ | GPU servers, many users | PagedAttention, continuous batching |
    | **MLX** | MLX quantised | Apple Silicon | Unified memory, fast on M-series |
    | **Transformers** | HF safetensors | Research, fine-tuning | Flexible, not a serving engine |
    | **SGLang** | HF, quantised | High-throughput serving | Radix attention for shared prefixes |

    For this course: start with **Ollama** because it gets you from zero to a
    working endpoint in one command. Move to **vLLM** when you need throughput,
    not before.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## The real bottleneck: memory bandwidth

    Generating a token requires reading **every weight** once. So decode speed
    is bounded by how fast memory can feed the compute units, not by FLOPs:

    ```
    tokens/second  ≈  memory bandwidth (GB/s) / model size in memory (GB)
    ```

    | Hardware | Memory | Bandwidth | 8B Q4 (~5 GB), ideal |
    |---|---|---|---|
    | M-series laptop | Unified, 16–128 GB | 70–540 GB/s | ~15–110 tok/s |
    | RTX 4090 | 24 GB GDDR6X | ~1000 GB/s | ~190 tok/s |
    | A100 80 GB | 80 GB HBM2e | ~2000 GB/s | ~390 tok/s |
    | H100 80 GB | 80 GB HBM3 | ~3350 GB/s | ~650 tok/s |

    Ideal numbers assume perfect utilisation; 50–70 % is realistic. This is
    why a **70B model at 4 bits (40 GB) does not run on a 24 GB GPU at all**,
    and why offloading layers to system RAM collapses throughput: you are now
    limited by PCIe or CPU memory bandwidth.
    """
    )
    return


@app.cell
def _(mo):
    bandwidth = mo.ui.slider(
        start=50, stop=3500, step=50, value=1000, label="Memory bandwidth (GB/s)"
    )
    efficiency = mo.ui.slider(
        start=30, stop=90, step=5, value=60, label="Realistic efficiency (%)"
    )
    size = mo.ui.slider(
        start=1, stop=160, step=1, value=5, label="Model size in memory (GB)"
    )
    mo.vstack(
        [
            mo.md(
                r"""
    ## Calculator: tokens per second

    A first-order estimate of single-stream decode speed. Use the model size
    from the previous calculator.
    """
            ),
            bandwidth,
            efficiency,
            size,
        ],
        gap=1,
    )
    return bandwidth, efficiency, size


@app.cell
def _(bandwidth, efficiency, size, mo):
    ideal = bandwidth.value / max(size.value, 0.1)
    realistic = ideal * efficiency.value / 100

    mo.vstack(
        [
            mo.hstack(
                [
                    mo.stat(value=f"{ideal:.0f}", label="Ideal tok/s"),
                    mo.stat(value=f"{realistic:.0f}", label="Realistic tok/s"),
                    mo.stat(
                        value=f"{3600 * realistic / 1e6:.1f}M",
                        label="Tokens per hour",
                    ),
                ],
                justify="start",
                gap=2,
            ),
            mo.callout(
                mo.md(
                    f"""
    **Rule of thumb:** keep model size below half the available memory. If an
    8B model is 5 GB on a 16 GB laptop, the KV cache and the rest of the system
    still have 11 GB to work with.

    At {realistic:.0f} tok/s, a 2,000-token answer takes about
    {2000 / max(realistic, 1):.0f} seconds. For interactive use, below
    ~15 tok/s starts to feel slow; below ~5 tok/s it is batch work, not chat.
    """
                ),
                kind="info",
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Latency versus throughput

    Two phases, two bottlenecks:

    - **Prefill** — process the prompt. Compute-bound and parallel. A long
      prompt is expensive once, then cached.
    - **Decode** — generate tokens one at a time. Bandwidth-bound and serial.

    Batching changes the economics. Serving 32 requests together reads the
    weights once for 32 tokens instead of once per token, so **throughput**
    rises sharply while **per-token latency** rises slightly.

    | Goal | Metric | Technique |
    |---|---|---|
    | Snappy chat | Time to first token, tok/s | Small model, short prompt, no batching |
    | Many users | Tokens/s aggregate | Continuous batching (vLLM, SGLang) |
    | Long documents | Prefill cost | Prompt caching, chunking |
    | Agents | Cost per task | Fewer steps, smaller model, cached prefix |

    An agent is a **latency multiplication machine**: ten sequential model
    calls at two seconds each is twenty seconds before any work is visible.
    """
    )
    return


@app.cell
def _(mo):
    hw_cost = mo.ui.slider(
        start=500, stop=25000, step=500, value=4000, label="Hardware cost (USD)"
    )
    lifetime_days = mo.ui.slider(
        start=180, stop=1825, step=5, value=730, label="Useful lifetime (days)"
    )
    tokens_day = mo.ui.slider(
        start=1, stop=200, step=1, value=10, label="Generated tokens per day (millions)"
    )
    api_price = mo.ui.slider(
        start=0.1, stop=15.0, step=0.1, value=3.0, label="API price (USD per 1M output tokens)"
    )
    mo.vstack(
        [
            mo.md(
                r"""
    ## Calculator: local versus hosted cost

    Compares **hardware amortisation + electricity** against a per-token API
    bill. It deliberately ignores your time, and treats electricity as the only
    running cost.
    """
            ),
            mo.hstack([hw_cost, lifetime_days], justify="start", gap=2),
            tokens_day,
            api_price,
        ],
        gap=1,
    )
    return api_price, hw_cost, lifetime_days, tokens_day


@app.cell
def _(api_price, hw_cost, lifetime_days, mo, tokens_day):
    # Assume a 300 W machine at 0.15 USD/kWh, 8 active hours per day.
    watts, hours, kwh_price = 300, 8, 0.15
    electricity_day = watts / 1000 * hours * kwh_price
    hardware_day = hw_cost.value / lifetime_days.value

    local_day = electricity_day + hardware_day
    api_day = tokens_day.value * api_price.value
    saving_day = api_day - local_day

    if saving_day <= 0:
        verdict = (
            f"At {tokens_day.value}M tokens/day the API costs "
            f"**{api_day:,.2f} USD/day** and local costs "
            f"**{local_day:,.2f} USD/day**. "
            "Hosted wins: you would need more volume, or a reason other than cost."
        )
    else:
        break_even = hw_cost.value / saving_day
        verdict = (
            f"API: **{api_day:,.2f} USD/day**. "
            f"Local: **{local_day:,.2f} USD/day** "
            f"(hardware {hardware_day:,.2f} + power {electricity_day:,.2f}). "
            f"Hardware pays back in about **{break_even:.0f} days**, or "
            f"{break_even / 365:.1f} years."
        )

    mo.vstack(
        [
            mo.callout(mo.md(verdict), kind="info"),
            mo.md(
                r"""
    The break-even is far longer than most people expect. The case for local
    inference is usually **privacy, control, or offline operation** — cost is a
    bonus at high steady volume, never the headline.

    Also note what this ignores: a hosted frontier model may solve in one call
    what a local model needs five attempts to solve. **Cost per task**, not
    cost per token, is the number that matters.
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
    ## The capability gap is not uniform

    Local models are weakest exactly where agents need them most.

    | Task | Local 8B at Q4 | Frontier hosted |
    |---|---|---|
    | Summarise a document | Good | Excellent |
    | Extract fields into JSON | Good with a schema | Excellent |
    | Classify / route | Often sufficient | Overkill |
    | Multi-step tool use | Fragile | Reliable |
    | Long-horizon planning | Poor | Usable |
    | Code changes across files | Weak | Strong |

    Design implication: **put the local model where the task is narrow**, and
    keep the agent loop short. If you need twenty reliable steps, either use a
    frontier model or restructure the task into a workflow with fewer decisions.

    Week 9 covers model selection and how to test portability properly.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Practical: serve, query, compare

    **1. Serve a local model**

    ```bash
    ollama pull llama3.1:8b-instruct-q4_K_M
    ollama serve                     # http://localhost:11434
    ollama run llama3.1:8b-instruct-q4_K_M "Explain KV caching in two sentences."
    ```

    **2. Use it through an OpenAI-compatible client**

    ```python
    from openai import OpenAI

    local = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    reply = local.chat.completions.create(
        model="llama3.1:8b-instruct-q4_K_M",
        messages=[{"role": "user", "content": "..."}],
    )
    ```

    **3. Measure, do not guess**

    Send the **same prompts** to the local model and a hosted baseline. For
    each run record:

    - wall-clock latency and time to first token,
    - prompt and completion tokens,
    - tokens/second,
    - peak memory (`ollama ps`, `nvidia-smi`, Activity Monitor),
    - a blind quality score on a 1–5 rubric.

    Repeat each prompt at least three times. Report the median and the spread;
    a single run tells you almost nothing.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## What to write in your report

    | Quantity | How to obtain it | Why it matters |
    |---|---|---|
    | Model size in memory | `ollama ps`, or weights + KV estimate | Predicts fit on other hardware |
    | Decode speed | completion tokens / decode seconds | User experience |
    | Time to first token | client timer | Perceived responsiveness |
    | Cost per task | tokens × price, or kWh × price | Comparison with hosted |
    | Quality | rubric, same prompts, repeated | The only thing that justifies the cost |
    | Failure modes | read the transcripts | Quantisation and context limits show up here |

    A useful conclusion sounds like: *"At 12 tok/s the local 8B model matched
    the hosted model on extraction (18/20 vs 19/20) but failed 6/20 multi-step
    tool calls, mostly by emitting malformed JSON. It is suitable for the
    extraction stage, not for the agent loop."*
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Recap

    - **Memory is the first constraint**: weights ≈ parameters × bits / 8, and
      the KV cache grows with context.
    - **4–5 bit quantisation** is the practical default; below that, agentic
      reliability degrades before benchmark scores do.
    - **Decode is bandwidth-bound**: tokens/second ≈ bandwidth / model size.
      This predicts performance better than any spec sheet.
    - **Batching trades latency for throughput**; agents multiply latency, so
      keep loops short.
    - **Local is rarely cheaper at low volume.** Choose it for privacy, control,
      and reproducibility — and always measure cost per *task*.

    **Next week:** prompting and context engineering — how to make a given
    model, local or hosted, behave reliably enough to build on.

    **Reading**

    - Ollama documentation, *OpenAI compatibility* and *Modelfile* reference.
    - llama.cpp, *Quantisation* README (`Q4_K_M`, `Q5_K_M`, `K-quants`).
    - vLLM, *PagedAttention* paper: Kwon et al. (2023), arXiv:2309.06180.
    - Databricks, *LLM Inference Performance Engineering: Best Practices*.
    """
    )
    return


if __name__ == "__main__":
    app.run()
