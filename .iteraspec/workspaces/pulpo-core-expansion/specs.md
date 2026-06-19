# Product Specifications: Pulpo Core Expansion

## Overview
This cycle expands the "Pulpo" Git Client MVP by integrating essential repository management capabilities (branches, stashes) and significantly improving the visualization of history (visual graphs and diffs).

## Functional Requirements (RF)
- **RF01 (Branch Switching)**: The system must allow the user to view available local branches and checkout a different branch from the UI.
- **RF02 (Branch Creation)**: The system must provide a mechanism to create a new branch starting from the active commit or branch.
- **RF03 (Stash Management)**: The system must provide UI buttons to save uncommitted changes (`git stash`) and apply/remove them (`git stash pop`).
- **RF04 (Commit Diff Viewer)**: Upon selecting a commit from the sidebar, the details pane must display the modified files and a classic visual diff. Removed lines must be highlighted in red, and added lines in green.
- **RF05 (Visual Tree Graph)**: The commit history sidebar must display structural branch lines (bifurcations and merges) graphically using SVG, Canvas, or advanced DOM manipulation, replacing the linear placeholder.

## Non-Functional Requirements (RNF)
- **RNF01 (Asynchronous Git)**: All git commands (`checkout`, `branch`, `stash`, `diff`) must be executed asynchronously in the Node.js Main process.
- **RNF02 (Strict UI Decoupling)**: UI templates for diffs, branch lists, and modals must reside entirely in HTML/CSS. JavaScript should only clone and inject data via data-attributes.
- **RNF03 (Aesthetics)**: The new diff viewer and branch controls must adhere to the established "premium minimalist dark mode" design system.
