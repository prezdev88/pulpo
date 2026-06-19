# System Architecture: Pulpo Tabs

## Overview
This architectural document outlines the technical implementation for the Multi-Project Tabs feature. The core challenge is maintaining state isolation between repositories without adding significant complexity to the Electron Main process.

## 1. Frontend State Management (`app.js`)
Instead of a single `activeRepoPath` variable, the application will manage a global `TabManager` pattern.
- **State Object**:
  ```javascript
  const state = {
      tabs: [], // Array of { id: string, path: string, name: string }
      activeTabId: null
  };
  ```
- **Session Persistence**: 
  - `localStorage.setItem('pulpo-tabs', JSON.stringify(state.tabs))`
  - `localStorage.setItem('pulpo-active-tab', state.activeTabId)`
- **Switching Strategy**:
  - We will implement a "Re-render on Switch" pattern. When a tab is selected, `app.js` will immediately update the active tab ID and call `loadRepoData(tab.path)`. Since backend operations are asynchronous and fast, this avoids the high memory overhead of maintaining multiple hidden DOM trees while still feeling instantaneous.

## 2. Main Process & IPC Updates (`main.js` & `preload.js`)
- **Native Menu Integration**:
  - A custom `Menu` will be configured in `main.js` using Electron's `Menu.buildFromTemplate`.
  - It will include a "File -> Open Repository" option.
  - A new IPC channel `window.webContents.send('app:onOpenRepository')` will notify the renderer.
  - `preload.js` will expose `window.api.onOpenRepository(callback)` so `app.js` can react and trigger the dialog.

## 3. UI Component Hierarchy (`index.html` & `style.css`)
- **Tabs Bar**:
  - A new `<nav class="tabs-bar">` will be inserted inside `main`, right above the `#commits-view` container.
  - Structure:
    ```html
    <nav class="tabs-bar" id="tabs-bar">
        <div class="tabs-container" id="tabs-container">
            <!-- Tabs will be injected here -->
        </div>
        <button id="new-tab-btn" class="glass-btn">+</button>
    </nav>
    ```
- **CSS Additions**: Flexbox layout for the horizontal scrollable tabs container. The active tab will have a distinct background color (`rgba(255, 255, 255, 0.1)`) and border bottom, while inactive tabs will remain slightly dimmed.

## 4. Edge Cases & Error Handling
- **Closing the Last Tab**: Will hide `#commits-view` and show `#landing-card`.
- **Duplicate Prevention**: If the user tries to open a repository that is already in the tabs list, the app will just switch to the existing tab.
- **Stale Local Storage**: If a stored path no longer exists when the app restarts, the `loadRepoData` try/catch block will catch the failure, and we will gracefully remove the invalid tab and notify the user.
