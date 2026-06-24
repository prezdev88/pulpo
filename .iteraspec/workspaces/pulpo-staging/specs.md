# Product Specifications: Pulpo Staging & Committing

## Overview
This cycle introduces a comprehensive VS Code-style "Source Control" tab. It expands the read-only git client into a fully functional authoring tool by allowing users to selectively stage files, review uncommitted diffs, and create new commits without leaving the application.

## Functional Requirements (RF)
- **RF01 (Sidebar Navigation)**: The sidebar must support switching between "History" (commits) and "Staging" (source control) views.
- **RF02 (Live Git Status)**: The Staging view must categorize uncommitted work into "Staged Changes" and "Changes" (unstaged/untracked files), updating automatically when files change on disk or when the user takes action.
- **RF03 (Stage / Unstage)**: Users must be able to stage individual files (`git add <file>`), unstage them (`git reset HEAD <file>`), or apply bulk actions (Stage All / Unstage All).
- **RF04 (Commit Authoring)**: The UI must provide a text area for a commit message and a button to execute `git commit -m`. Upon successful commit, the view should refresh and the new commit should appear in the History view.
- **RF05 (Live Diffs)**: Clicking an unstaged file must show its real-time diff (`git diff <file>`) in the main right panel. Clicking a staged file must show its cached diff (`git diff --cached <file>`).

## Non-Functional Requirements (RNF)
- **RNF01 (Asynchronous Git)**: All git authoring operations must be executed asynchronously via Node.js `child_process`.
- **RNF02 (Premium Aesthetic)**: The new Staging UI must integrate seamlessly with the existing dark mode, utilizing custom scrollbars, glassmorphism containers, and smooth hover state transitions for the `+`/`-` action buttons.
- **RNF03 (State Isolation)**: The active sidebar mode (History vs Staging) and the drafted commit message must be isolated per tab. Switching to another repository tab should not mix commit messages.

## Architectural Decisions
- `app.js` will orchestrate the view toggling. We will add a `<div id="staging-view">` next to `<div id="history-view">` (which wraps the current commit tree).
- `preload.js` will expose new endpoints: `git:status`, `git:stage`, `git:unstage`, `git:commit`, and `git:getLiveDiff`.
