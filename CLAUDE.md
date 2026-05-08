# CLAUDE.md

## Project Context
This repository supports the Johns Hopkins Agentic AI course labs and projects.
It contains notebooks, small Python apps, and project artifacts that build from Python fundamentals to retrieval-augmented generation and agentic system design.

Primary goal for this Claude Cowork setup:
- Help with coursework implementation, debugging, and iteration.
- Keep outputs practical, reproducible, and aligned with the weekly learning objectives.
- Prefer minimal, correct changes over broad refactors.
- Help manage completion tasks for course materials, quiz submissions, and project deadlines.

## Course Structure in This Repo
- Pre-Work Session 1
  - Python essentials case study notebook.
- Week 1 - Python Refresher for Agentic AI
  - Debugging and shopping cart management notebooks.
  - Small inventory app in Week 1 - Python Refresher for Agentic AI/ai-inventory.
- Week 2 - Introduction to Large Language Models
  - Prompt engineering fundamentals notebooks.
- Week 3 - Prompt Engineering Techniques and RAG
  - DSPy introduction, RAG notebooks, and content folder with research papers.
- Week 4 - Project 1 - DualLens Analytics
  - Project notebook and company initiative materials.
- Week 6 - Introduction to Agentic AI Design
  - Agentic RAG notebooks and supporting data and JSON assets.

## Current Working Focus
The active notebook is in Week 6 and centered on Agentic RAG and smolagents workflows.
When helping in this repository, prioritize:
- Notebook-safe changes that do not break execution order.
- Clear explanations of why a change is needed.
- Quick verification steps after edits.

## Course Operations and Deadlines
- Video content should be completed before Mentored Learning Sessions each Saturday at 2:30 PM (user local time).
- Quizzes should be submitted before the following Monday.
- Project deadlines should be actively tracked from the cohort schedule.
  - Current schedule milestones: Project-1 (19-Apr), Project-2 (7-Jun), Project-3 (26-Jul), and pre-deployment operationalization deliverable (2-Aug).
  - Treat schedule dates as source-of-truth but potentially changeable if the program office updates timing.

## Environment and Execution Notes
- OS: macOS
- Shell: zsh
- Python virtual environment is typically activated from .venv-1.
- Prefer the existing environment and installed dependencies before introducing new ones.
- Keep dependency additions explicit and minimal.

## Working Agreements for Claude Cowork
- Preserve existing folder structure and naming used by course materials.
- Avoid rewriting large notebook sections unless requested.
- If a fix is uncertain, present assumptions and a small, testable change first.
- Keep task-planning outputs compatible with future task tracking in TASKS.md.
- For coding tasks:
  - Add concise comments only where logic is non-obvious.
  - Keep function and variable names readable and instructional.
  - Do not remove learner-facing context from notebooks.
- For debugging tasks:
  - Identify root cause first.
  - Propose the smallest viable fix.
  - Provide a short validation checklist.

## Preferred Output Style
- Be concise and practical.
- Use step-by-step actions for labs.
- Include copy-paste-ready commands or code when useful.
- Call out risks or side effects before making broader changes.

## Suggested Quick Start Tasks
1. Validate the active Week 6 notebook cell-by-cell and capture any failing cells.
2. Verify required imports and package availability in the current environment.
3. Add lightweight utility helpers only if they improve clarity across repeated notebook steps.
4. Keep all changes localized to the week or project currently being worked on.
5. Build and maintain a short task checklist for videos, quizzes, and project deadlines to prepare for later TASKS.md automation.

## Out of Scope Unless Requested
- Reorganizing the full repository.
- Large style-only rewrites.
- Converting notebook-heavy workflows into a full production application.

## Maintainer Note
If new weeks or projects are added, update this file so Claude Cowork keeps course context accurate.
