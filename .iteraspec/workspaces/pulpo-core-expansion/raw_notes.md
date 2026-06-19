# Raw Notes: Pulpo Core Expansion

## Context
The user wants to expand the MVP of "Pulpo" (Git Client) with standard, robust desktop client features.

## Feature Requests
1. **Branch Management**
   - Ability to switch branches directly from the application.
   - Ability to create new branches.

2. **Stash Management**
   - Support for `git stash` (save changes).
   - Support for `git stash pop` (apply saved changes).

3. **Commit Details & Diff Viewer**
   - Show details of a selected commit.
   - Display a classic visual diff of modified files.
   - Red highlighting for removed/modified lines.
   - Green highlighting for added lines.
   - Expected standard desktop Git client UX for code comparison.

4. **Visual Commit Graph (Carried over from MVP)**
   - Display branch bifurcations and merges graphically.

## Constraints & Aesthetics
- Maintain the Premium, Minimalist, Glassmorphism design system.
- Maintain Strict UI Decoupling (Clean Architecture, RNF05).
- All git interactions must be asynchronous and non-blocking.

## Future Scope (Next Iteration)
- **Multi-Project Support**: Allow opening multiple projects simultaneously using tabs or a tabbed interface.
