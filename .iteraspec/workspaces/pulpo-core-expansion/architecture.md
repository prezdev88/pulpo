# Architecture Design: Pulpo Core Expansion

## Design Philosophy
We continue to use the Clean Architecture paradigm (Core Use Cases -> Main IPC -> Preload API -> Renderer UI).
The strict decoupling rule (RNF02) mandates that all new visual components (diff viewer, branch modals) must be defined as `<template>` in HTML, while JavaScript handles the structural injection.

## Component Updates

### 1. Core Layer (Use Cases)
We will introduce the following asynchronous Node.js modules using `child_process.exec`:
- `getBranchesUseCase.js`: Executes `git branch` to list local branches and detect the active one.
- `checkoutBranchUseCase.js`: Executes `git checkout <branch>`.
- `createBranchUseCase.js`: Executes `git checkout -b <branch>`.
- `stashUseCase.js`: Executes `git stash` and `git stash pop`.
- `getCommitFilesUseCase.js`: Executes `git diff-tree --no-commit-id --name-only -r <hash>` to list modified files.
- `getFileDiffUseCase.js`: Executes `git diff <hash>^ <hash> -- <file>` to extract the precise diff of a single file.

### 2. Main & Preload Layers (IPC Bridge)
- `main.js`: Add IPC handlers (`git:getBranches`, `git:checkout`, `git:createBranch`, `git:stash`, `git:stashPop`, `git:getCommitFiles`, `git:getFileDiff`).
- `preload.js`: Map these handlers to `window.api`.

### 3. Renderer Layer (UI)
- **index.html & style.css**:
  - Add a Top Navigation Bar or Dropdown in the sidebar to show the active branch and allow switching/creating branches.
  - Add Stash control buttons (Save, Pop).
  - Transform the right panel (`commit-details-pane`) into a Split View:
    - Left/Top section: List of files modified in the commit.
    - Right/Bottom section: Visual code viewer rendering lines with a `<template id="diff-line-template">`.
- **app.js**:
  - Add event listeners for branch switching and creation.
  - Add logic to fetch and display commit files when a commit row is clicked.
  - Add logic to request a file's diff and paint the lines (red for `-`, green for `+`) based on the diff output.
  - Replace the linear vertical line logic with an HTML5 `<canvas>` (or SVG) that visually calculates parent-child branch structures.
