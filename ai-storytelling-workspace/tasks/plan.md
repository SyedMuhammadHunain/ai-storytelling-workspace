# Implementation Plan: AI Storytelling Workspace MVP

## Overview

Building a Python CLI orchestrator that demonstrates the 15-agent workflow for AI-assisted book writing. This MVP uses mock agents with simple outputs to validate the orchestration pattern: proper agent sequencing (sequential vs parallel), Story Bible state management, and human checkpoint handling. Real AI integration is out of scope.

## Architecture Decisions

- **Language:** Python 3.10+ for simplicity and rapid prototyping
- **Story Bible:** JSON file-based storage for easy inspection and debugging
- **Agent Model:** Base class with mock implementations, designed for easy swap to real AI later
- **Orchestration:** Sequential execution with explicit parallel batching where specified
- **Human Checkpoints:** CLI prompts that pause execution and wait for user input
- **Logging:** Console output showing agent execution flow and Story Bible updates

## Task List

### Phase 1: Foundation (Tasks 1-4)

- [x] **Task 1:** Set up project structure and dependencies
- [x] **Task 2:** Implement Story Bible data structures and persistence
- [x] **Task 3:** Implement base Agent class and mock agent framework
- [x] **Task 4:** Implement human checkpoint system

**Checkpoint: Foundation**
- [ ] Story Bible can be created, read, updated, and persisted
- [ ] Base agent can execute and log output
- [ ] Human checkpoint can pause and resume execution
- [ ] All unit tests pass

### Phase 2: Setup Agents (Tasks 5-8)

- [x] **Task 5:** Implement Intake Agent (captures user input, creates Book Brief)
- [x] **Task 6:** Implement Concept Agent (expands brief into premise)
- [x] **Task 7:** Implement Worldbuilding Agent (creates world rules, timeline)
- [x] **Task 8:** Implement Character Agent (creates character profiles)

**Checkpoint: Setup Agents**
- [ ] All setup agents execute and update Story Bible correctly
- [ ] Mock outputs are realistic enough to validate pattern
- [ ] Human checkpoint 1-3 work correctly

### Phase 3: Architecture & Drafting Agents (Tasks 9-11)

- [x] **Task 9:** Implement Plot Architect Agent (creates chapter outline)
- [x] **Task 10:** Implement Chapter Drafting Agent (generates mock chapter text)
- [x] **Task 11:** Implement Continuity Agent (checks for contradictions)

**Checkpoint: Drafting**
- [ ] Chapter drafting can run in parallel batches
- [ ] Story Bible accumulates chapter deltas correctly
- [ ] Continuity agent can flag mock issues

### Phase 4: Editing Agents (Tasks 12-15)

- [ ] **Task 12:** Implement Dialogue/Voice Agent (checks character voice)
- [ ] **Task 13:** Implement Developmental Editor Agent (evaluates structure)
- [ ] **Task 14:** Implement Line/Copy Editor Agents (prose and grammar)
- [ ] **Task 15:** Implement Proofreader Agent (final surface check)

**Checkpoint: Editing**
- [ ] All editing agents execute in correct order
- [ ] Mock feedback is generated and logged

### Phase 5: Assembly & Finalization (Tasks 16-19)

- [ ] **Task 16:** Implement Front/Back Matter Agents (title page, TOC, etc.)
- [ ] **Task 17:** Implement Compilation Agent (assembles manuscript)
- [ ] **Task 18:** Implement QA Agent (validates completeness)
- [ ] **Task 19:** Implement Export Agent (outputs to files)

**Checkpoint: Assembly**
- [ ] Full manuscript can be compiled
- [ ] Export produces readable output files

### Phase 6: Orchestration & CLI (Tasks 20-22)

- [ ] **Task 20:** Implement Master Orchestrator (coordinates all agents)
- [ ] **Task 21:** Implement CLI entry point with argument parsing
- [ ] **Task 22:** Add comprehensive logging and progress indicators

**Checkpoint: Integration**
- [ ] Full workflow runs end-to-end from CLI
- [ ] All 15 agents execute in correct order
- [ ] Human checkpoints pause at correct points
- [ ] Story Bible evolves correctly throughout

### Phase 7: Testing & Documentation (Tasks 23-25)

- [ ] **Task 23:** Write integration tests for full workflow
- [ ] **Task 24:** Create README with usage instructions
- [ ] **Task 25:** Add example run output and Story Bible samples

**Checkpoint: Complete**
- [ ] All tests pass
- [ ] Documentation is clear and complete
- [ ] Example outputs demonstrate the pattern

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Story Bible state management complexity | High | Start with simple JSON, add versioning only if needed |
| Parallel execution coordination | Medium | Use simple sequential batching, not true async |
| Mock outputs too simplistic | Low | Focus on demonstrating pattern, not content quality |
| Human checkpoint UX unclear | Medium | Use clear prompts with numbered options |

## Open Questions

- Should we support resuming from a checkpoint if interrupted?
- Do we need Story Bible versioning/history in the MVP?
- Should parallel chapter drafting be truly async or just batched sequential?

## Success Criteria

The MVP is complete when:
1. Running `python cli.py` executes all 15 agents in correct order
2. Story Bible JSON file shows proper state evolution
3. Human checkpoints pause at 6 defined points
4. Console logs clearly show agent sequencing and parallel batches
5. Final output includes compiled manuscript and Story Bible
6. README explains how to run and what to expect
