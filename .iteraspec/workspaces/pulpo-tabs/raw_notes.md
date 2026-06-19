# Raw Notes: Pulpo Tabs (Multi-Project Support)

## Context
The user wants to add multi-project support to Pulpo through a tabbed interface.

## Answers from Discovery
1. **Location**: The tab bar will be located directly above the main commits view panel ("encima del panel donde se ven los cambios"). It should span the application width to act as a global repository switcher.
2. **Tab Creation**: A fixed "+" button at the end of the tab list will directly open the folder selection dialog.
3. **Persistence**: The application must remember the opened repositories. If closed and reopened, the previous tabs (and the active one) should be restored.
4. **Independent State**: Each tab operates as an isolated workspace. Switching tabs should restore the view (active branch, selected commit, UI state) for that specific repository.
5. **Native Menu Integration**: The Electron application menu must be updated to include a "File -> Open Local Repository" option (or similar) that also opens the dialog and creates a new tab.

## Constraints & Aesthetics
- The tabs must match the "Premium, Minimalist, Dark Mode (Glassmorphism)" aesthetic.
- The state persistence should be handled efficiently (e.g., using `localStorage` in the renderer or `electron-store` in the main process).
- Native menu integration requires IPC communication from Main to Renderer to trigger the tab creation.
