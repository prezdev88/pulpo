# Raw Notes: Pulpo Staging & Committing

## Context
The user wants to implement a full VS Code-style "Source Control" staging area, allowing the user to view unstaged files, stage/unstage them, and create new commits directly from the application. The user has delegated the exact UX/UI decisions to the AI, requesting "the best possible look".

## Design Decisions (AI Delegated)
1. **Sidebar Modes**: The left sidebar will now have two modes: "History" (the current commit tree) and "Source Control". A sleek icon-based toggle at the top of the sidebar will allow switching between these modes.
2. **Source Control View Structure**:
   - **Commit Box**: A text area for the commit message with a prominent "Commit" button at the top of the sidebar.
   - **Staged Changes**: An accordion-style list showing files currently in the index (`git diff --cached --name-status`).
   - **Changes**: An accordion-style list showing modified/untracked files (`git status -s`).
3. **Interactions**:
   - Hovering over a file reveals quick action buttons (`+` to stage, `-` to unstage).
   - Global buttons next to the headers to "Stage All" or "Unstage All".
   - Clicking a file displays its real-time uncommitted diff in the main right-hand panel.

## Technical Constraints
- Must maintain the Premium Dark Glassmorphism aesthetic.
- All new git commands (`status`, `add`, `reset`, `commit`, live `diff`) must be asynchronous and exposed via `ipcMain` / `preload.js`.
- State isolation per tab must be respected (each tab has its own staging view state).
