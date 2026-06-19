# Product Specifications: Pulpo Tabs (Multi-Project Support)

## Overview
This feature expands the Pulpo Git Client by allowing users to open and manage multiple local Git repositories simultaneously. A global tab bar will be introduced to facilitate seamless switching between active projects, while maintaining the independent state and context of each repository.

## Functional Requirements (RF)
- **RF01 (Tab Bar UI)**: The system must display a horizontal tab bar above the main view. Each tab will represent an opened repository, displaying its folder name.
- **RF02 (Add New Tab)**: A fixed `+` button at the end of the tab list must open the directory selection dialog. Upon selecting a valid Git repository, a new tab is created and focused.
- **RF03 (Tab Switching & Isolation)**: Clicking an inactive tab must switch the view to that repository. The application must maintain independent states for each tab (e.g., active branch, selected commit, diff view).
- **RF04 (Close Tab)**: Each tab must have a close (`x`) button. Closing a tab removes it from the workspace. If the active tab is closed, the system should automatically focus an adjacent tab (or show the landing page if it was the last tab).
- **RF05 (Session Persistence)**: The application must remember the list of opened tabs and the currently active tab across application restarts. 
- **RF06 (Native Menu Integration)**: The native Electron Application Menu must include a "File -> Open Repository..." option (or similar) that triggers the same flow as the `+` button in the tab bar.

## Non-Functional Requirements (RNF)
- **RNF01 (Decoupled Persistence)**: State persistence (saving open tabs) should be handled cleanly, preferably using `localStorage` in the renderer process to maintain the clean architecture and decouple it from main process disk I/O where unnecessary.
- **RNF02 (Aesthetics)**: The tabs must adhere to the "Premium, Minimalist, Dark Mode" design. Active tabs should have a subtle glowing border or distinct background, while inactive tabs should blend into the glassmorphism aesthetic.
- **RNF03 (Performance)**: Switching tabs should be instantaneous. The DOM should ideally retain the state, or re-render quickly without re-fetching static git history unless requested.

## Initial Architectural Decisions
- The `index.html` will be restructured to include a `<nav class="tabs-bar">` above the `#commits-view` and `#landing-card`.
- The `app.js` will maintain an array of tab objects (e.g., `[{ path: '/repo1', name: 'repo1', ... }]`) and sync it with `localStorage`.
- A new IPC channel or menu event listener will be needed to handle the native "Open Repository" menu item and broadcast it to the renderer.
