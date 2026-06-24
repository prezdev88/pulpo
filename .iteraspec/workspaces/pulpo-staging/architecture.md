# System Architecture: Pulpo Staging & Source Control

## Overview
This document defines the architecture to support authoring commits and managing the staging area natively within the application.

## 1. Core Git Operations (Backend Use Cases)
We will create five new isolated use cases under `src/core/`:
- **`getStatusUseCase.js`**:
  - Executes `git status --porcelain` to identify modified, deleted, and untracked files.
  - Returns a structured object: `{ staged: [], unstaged: [] }`.
- **`stageFilesUseCase.js`**:
  - Executes `git add <file>` (or `git add .` for all).
- **`unstageFilesUseCase.js`**:
  - Executes `git reset HEAD <file>` (or `git reset HEAD` for all).
- **`commitChangesUseCase.js`**:
  - Executes `git commit -m "<message>"`.
- **`getLiveDiffUseCase.js`**:
  - Executes `git diff <file>` for unstaged files.
  - Executes `git diff --cached <file>` for staged files.

## 2. IPC Communication (`main.js` & `preload.js`)
The `preload.js` bridge will be expanded with the following endpoints:
- `window.api.getStatus(repoPath)`
- `window.api.stageFile(repoPath, file)`
- `window.api.unstageFile(repoPath, file)`
- `window.api.commitChanges(repoPath, message)`
- `window.api.getLiveDiff(repoPath, file, isStaged)`

## 3. UI Component Architecture (`index.html`)
The existing `#commits-sidebar` will be refactored to host a mode toggle and two distinct views:
```html
<aside class="commits-sidebar">
  <div class="sidebar-toggle-bar">
    <button id="mode-history-btn" class="active">🕒 History</button>
    <button id="mode-staging-btn">📝 Source Control</button>
  </div>
  
  <div id="history-view-container">
    <!-- Existing branches and commit graph -->
  </div>
  
  <div id="staging-view-container" class="hidden">
    <div class="commit-box">
      <textarea id="commit-message-input" placeholder="Message (Cmd+Enter to commit)"></textarea>
      <button id="commit-execute-btn">Commit</button>
    </div>
    
    <div class="accordion">
      <h4>Staged Changes <button class="unstage-all-btn">-</button></h4>
      <ul id="staged-files-list"></ul>
    </div>
    
    <div class="accordion">
      <h4>Changes <button class="stage-all-btn">+</button></h4>
      <ul id="unstaged-files-list"></ul>
    </div>
  </div>
</aside>
```

## 4. State Isolation (`app.js`)
To ensure states don't bleed across repositories:
- The `tabState.tabs` object will be expanded to include: `{ id, path, name, commitMessage, activeSidebarMode }`.
- Switching tabs will persist the currently typed commit message into the tab object, and restore the destination tab's message into the `<textarea>`.
