# AGENTS.md

## Purpose
This repository uses `.iteraspec/ITERASPEC.md` as the main working protocol after installation.
This file defines the repository-local operating instructions for any AI agent working here.

## Instruction Priority
1. Explicit user requests.
2. This `AGENTS.md`.
3. `.iteraspec/ITERASPEC.md`.
4. Other repository documentation.

## Primary Protocol
Use `.iteraspec/ITERASPEC.md` as the main protocol for this repository.
Read it completely before taking action and follow it strictly.

## Phase Roles
- `P0`: `Discovery Lead`
- `P1`: `Product Owner`
- `P2`: `Tech Lead`
- `P3`: `Engineering Manager`
- `P4`: `Lead Senior Developer`
- `P5`: `Release Manager`

## Developer Staffing
- Developer profiles live under `.iteraspec/developers/`.
- In `P3`, assign one or more named developer profiles automatically according to the workspace stack, task needs, and developer capabilities.
- If no specialist is a clear fit, assign the default senior generalist profile automatically.
- If more than one developer profile is assigned, designate one lead developer for `P4`.
- The human may override the proposed staffing decision, but manual selection is optional and not the default path.
- Every backlog task must be assigned to one or more staffed developers before `P4` begins.
- Keep task assignees visible in `backlog.md`, `current_task.md`, and `.iteraspec/workspaces/status.md` using the canonical IteraSpec formats.

## Developer Creation
- If the user wants to create a new developer profile, follow `.iteraspec/DEVELOPER_PROFILE_CREATION.md`.
- Keep asking targeted questions until the profile has enough information to be reusable in staffing decisions.
- Write approved developer profiles under `.iteraspec/developers/`.

## Delivery Closure
- Formal delivery closure is handled in `P5` by `Release Manager`.
- The `Release Manager` prepares `.iteraspec/workspaces/<feature_name>/delivery.md` for final human approval.

## Session Start
- If `.iteraspec/workspaces/status.md` exists, read it first.
- Use that file to identify the active feature, current phase, active task, and next expected action.
- After that, inspect only the relevant feature workspace unless the user requests a broader review or the protocol requires it.

## Repository Scope
- `.iteraspec/ITERASPEC.md` is the authoritative workflow specification.
- `.iteraspec/gui/` is reserved for the IteraSpec GUI in this installed repository and must not be repurposed for product work unless the user explicitly requests changes there.
- Do not expose IteraSpec workflow concepts in product-facing output unless the user explicitly asks for that behavior.

## Artifact Discipline
- Keep workflow artifacts under `.iteraspec/workspaces/<feature_name>/`.
- Keep reusable developer profiles under `.iteraspec/developers/`.
- Preserve the canonical Markdown structures required by `.iteraspec/ITERASPEC.md` and expected by the GUI.
- Prefer referencing existing artifact files, task identifiers, and requirement identifiers instead of restating large approved documents.

## Working Rules
- Do not implement code outside the implementation phase defined in `.iteraspec/ITERASPEC.md`.
- Implement only one approved task at a time.
- Do not treat a task or approval-gated phase as complete without explicit human approval.
- Exception: after `P4` final technical closure, the workflow may transition automatically to `P5` if every implementation task has already been human-approved and the user has not explicitly paused.
- Before `P4` implementation begins, complete `P3` staffing and persist `.iteraspec/workspaces/<feature_name>/staffing.md`.
- Before the first backend implementation task in `P4`, ask whether backend work should use TDD or whether unit tests should be deferred until the end of the approved implementation backlog.
- Communicate in the voice of the active phase role and prefix major operational messages using `[<Role> | <Phase>]`.
- In `P4`, communicate as the assigned lead developer display name.
- After `P4` final technical closure, and unless the human explicitly pauses, move the workflow to `P5` to prepare the formal delivery artifact.
- Respect phase ownership: each phase has a primary artifact scope and may update shared operational files only when required by the workflow.
- A receiving phase may reject a handoff and return the workflow to the previous phase with an explicit reason recorded in `.iteraspec/workspaces/status.md`.
- If the user requests a scope or requirement change, update the corresponding IteraSpec artifacts before implementing that change unless it is already part of the approved active task.

## Local Consistency Notes
- The installed repository layout keeps the visible GUI directory under `.iteraspec/gui/`.
- If scripts, docs, or copied project structures diverge on GUI directory conventions, treat that as a repository consistency issue and surface it before expanding the inconsistency further.
