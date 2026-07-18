# AI Storytelling Workspace — Full Workflow Orchestration
### Built on IBM Bob (Multi-Agent, Subagents, Parallel Execution, Human Checkpoints)

---

## 0. Orchestration Model

One **Master Orchestrator Agent ("The Book Architect")** owns the pipeline. It never writes prose itself — it plans, dispatches subagents, enforces the Story Bible, and manages human checkpoints. Every other agent is a specialized subagent spawned by it, running in isolated context and returning only the relevant result (chapter text, report, or approval flag) back to the orchestrator — this is exactly Bob's subagent model, just repointed at narrative work instead of code.

**Shared state object: the Story Bible**
A persistent, versioned JSON/markdown store that every agent reads before working and writes to after. Contains: characters (traits, arcs, voice), locations, timeline/chronology, terminology/lore, plot threads, POV rules, tone/style guide. This is the single most important artifact — it's what keeps a 100k-word book internally consistent across dozens of agent calls.

**Model routing (Bob's multi-model routing, repurposed):**
- Heavy creative generation (drafting, dialogue) → most capable model
- Consistency/continuity checks, metadata tagging, summarization → lighter/faster model
- Style/line editing → mid-tier model tuned for precision, not creativity

---

## Phase 1 — Intake & Brief
**Agent: Intake Agent**
- Captures user input: genre, premise, target length, tone, comps ("like X meets Y"), POV, audience, content boundaries.
- Normalizes into a structured **Book Brief**.
- **Human Checkpoint 1:** user confirms/edits the brief before anything downstream runs.

## Phase 2 — Concept & Premise Development
**Agent: Concept Agent**
- Expands the brief into logline, premise, central conflict, theme, and 2–3 alternative concept directions.
- **Human Checkpoint 2:** user selects/approves final concept.

## Phase 3 — World & Character Bible (parallel subagents)
Runs in parallel, background tasks, results merged into the Story Bible:
- **Worldbuilding Agent** — setting, rules of the world, timeline, factions, geography.
- **Character Agent** — protagonist/antagonist/supporting cast: goals, flaws, arcs, voice signatures.
- **Continuity Agent (bootstrap pass)** — cross-checks worldbuilding vs. characters for contradictions before drafting starts.
- **Human Checkpoint 3:** approve Story Bible v1.

## Phase 4 — Story Architecture
**Agent: Plot Architect Agent**
- Builds full structure: act breaks, chapter-by-chapter outline, subplot threads, pacing map.
- Tags each chapter with: POV, goal, conflict, turn, word-count target.
- **Human Checkpoint 4:** outline approval — the most important gate, since everything downstream is expensive to redo.

## Phase 5 — Chapter Drafting (parallel subagent fan-out)
**Agent: Chapter Drafting Agents (N instances, one per chapter, isolated context)**
- Each subagent receives: its chapter's outline entry + relevant Story Bible slices only (not the whole bible — keeps context clean, per Bob's isolated-context design) + prior chapter's final paragraph for continuity of voice/tense.
- Drafts full chapter prose as a background task.
- Returns draft + a delta report (new facts introduced, characters/locations touched) back to orchestrator, which merges deltas into the Story Bible.

*Note: chapters can be drafted in parallel batches (e.g., 5 at a time) to save wall-clock time, but Bible-critical chapters (first appearances of major characters/twists) should run sequentially so later chapters can reference confirmed facts.*

## Phase 6 — Continuity & Consistency Pass
**Agent: Continuity Agent**
- Re-reads full manuscript-so-far against the Story Bible.
- Flags contradictions: timeline errors, eye-color-changed-halfway-through problems, dropped subplots, name/spelling drift.
- Produces a structured issue list, routed back to the relevant Chapter Drafting Agent for targeted revision (not a full rewrite).

## Phase 7 — Dialogue & Voice Pass
**Agent: Dialogue/Voice Agent**
- Reviews dialogue against each character's established voice signature.
- Flags characters who "sound the same" or drift out of voice.

## Phase 7.5 — Image Generation
**Agent: Image Generation Agent**
- Not every page gets an image. Fixed rule keeps this cheap and consistent:
  - Always: 1 cover image (from Cover Concept Agent's brief in Phase 12).
  - Interior: 1 image per act (opening, midpoint, climax) by default, plus any chapter the user manually flags as "high-visual."
- Uses one locked **style brief** (art style, palette, character appearance) stored in the Story Bible so all images stay visually consistent across the book.
- **Human Checkpoint (optional):** approve cover before it's locked into front matter.

## Phase 8 — Developmental Edit
**Agent: Developmental Editor Agent**
- Evaluates pacing, stakes, structural weaknesses, saggy middle, unearned resolutions — big-picture craft issues, not line-level.
- **Human Checkpoint 5:** user reviews developmental notes, approves which get actioned before line editing (expensive to line-edit prose that's about to be restructured).

## Phase 9 — Revision Pass
**Agent: Revision Orchestrator (sub-orchestrator)**
- Dispatches targeted rewrite subagents only to flagged chapters, re-runs Continuity Agent afterward to confirm nothing broke.

## Phase 10 — Line & Copy Edit
**Agent: Line Editor Agent** → prose rhythm, word choice, clarity, redundancy
**Agent: Copy Editor Agent** → grammar, punctuation, tense consistency, formatting rules
(Can run as two passes or two parallel subagents whose suggestions are merged and conflict-resolved by the orchestrator.)

## Phase 11 — Proofreading
**Agent: Proofreader Agent**
- Final surface-level pass: typos, spacing, straight vs. curly quotes, chapter numbering.

## Phase 12 — Front/Back Matter & Design
**Agent: Front Matter Agent** — title page, copyright page, dedication, TOC generation.
**Agent: Cover Concept Agent** — generates cover copy/brief (title treatment, back-cover blurb, tagline); if image generation is connected, produces cover art direction.
**Agent: Back Matter Agent** — acknowledgments, author bio, "about this book" blurb.

## Phase 13 — Compilation
**Agent: Compilation Agent**
- Assembles all chapters + front/back matter into a single manuscript in correct order.
- Applies consistent formatting (headings, scene breaks, page structure).
- Generates final word count, chapter list, and a change log (Bob's self-documenting/audit-trail behavior — every agent's contribution stays traceable).

## Phase 14 — Final QA
**Agent: QA Agent**
- Full-manuscript read-through validation: no missing chapters, no unresolved [TODO]/placeholder markers, no continuity flags left open.
- **Human Checkpoint 6 (final sign-off):** user approves the finished manuscript.

## Phase 15 — Export/Publish
**Agent: Export Agent**
- Outputs to requested formats (DOCX manuscript, EPUB, print-ready PDF).
- Packages the final Story Bible as a standalone deliverable too (useful for a sequel).

---

## Orchestration Diagram (logical flow)

```
Intake → Concept → [World || Character || Continuity-bootstrap] → Story Bible v1
      → Plot Architecture → [HUMAN GATE: Outline]
      → Chapter Drafting (parallel subagents, Bible deltas merged live)
      → Continuity Pass → Dialogue/Voice Pass
      → Image Generation (cover + select interior pages, [HUMAN GATE: Cover, optional])
      → Developmental Edit → [HUMAN GATE: Dev Notes]
      → Targeted Revision → Continuity Re-check
      → Line Edit + Copy Edit → Proofread
      → Front/Back Matter + Cover
      → Compilation → QA → [HUMAN GATE: Final Sign-off]
      → Export
```

## Key Design Principles Carried Over from Bob
1. **Isolated subagent context** — each chapter agent only sees what it needs, not the whole book, to avoid context bloat and cross-contamination of drafts.
2. **Shared persistent state (Story Bible)** — the one thing every agent must read/write; this is what most naive "AI writes a book" pipelines skip, and it's why they produce inconsistent novels.
3. **Human checkpoints at expensive-to-undo gates** — brief, concept, outline, dev-edit actions, and final sign-off. Not after every chapter (too slow) and not never (loses control).
4. **Background/parallel execution** for chapter drafting, sequential only where later chapters depend on facts established earlier.
5. **Auditability** — every agent's output and the Bible delta it caused should be logged, so you can trace exactly why chapter 14 says a character has a scar.

---

## Suggested Model Routing per Agent
| Agent | Recommended Model Tier |
|---|---|
| Concept, Plot Architect, Chapter Drafting, Developmental Editor | High-capability creative model |
| Worldbuilding, Character, Dialogue/Voice | High-capability creative model |
| Continuity, QA, Copy Editor, Proofreader | Fast/precise model (less creativity, more rule-checking needed) |
| Front/Back Matter, Compilation, Export | Lightweight model |
| Image Generation (cover + interior) | Dedicated image model, driven by one locked style brief |

---

## 15-Agent Quick Reference (grouped, MVP-friendly view)
| Stage | Agents | Count |
|---|---|---|
| Setup | Intake, Concept, Worldbuilding, Character | 4 |
| *Human gate: outline approval* | — | — |
| Drafting | Plot Architect, Chapter Drafting, Continuity, Dialogue/Voice | — (Plot Architect runs before gate; 3 run after) |
| Visuals | Image Generation | 1 |
| Editing | Developmental Editor, Revision, Line/Copy Editor, Proofreader | 4 |
| Assembly | Front/Back Matter (incl. Cover Concept), Compilation | 2 |
| Finalize | QA & Export | 1 |
| *Human gate: final sign-off* | — | — |

Total: 15 specialized agents, 2 human checkpoints.
