const { contextBridge, ipcRenderer } = require('electron');

// Expose safe APIs to the renderer process
contextBridge.exposeInMainWorld('api', {
  selectRepository: () => ipcRenderer.invoke('dialog:openDirectory'),
  getCommits: (repoPath) => ipcRenderer.invoke('git:getCommits', repoPath),
  getBranches: (repoPath) => ipcRenderer.invoke('git:getBranches', repoPath),
  checkoutBranch: (repoPath, branchName) => ipcRenderer.invoke('git:checkout', repoPath, branchName),
  createBranch: (repoPath, branchName, commitHash) => ipcRenderer.invoke('git:createBranch', repoPath, branchName, commitHash),
  deleteBranch: (repoPath, branchName) => ipcRenderer.invoke('git:deleteBranch', repoPath, branchName),
  stashChanges: (repoPath) => ipcRenderer.invoke('git:stash', repoPath),
  popStash: (repoPath) => ipcRenderer.invoke('git:stashPop', repoPath),
  getCommitFiles: (repoPath, hash) => ipcRenderer.invoke('git:getCommitFiles', repoPath, hash),
  getFileDiff: (repoPath, hash, file) => ipcRenderer.invoke('git:getFileDiff', repoPath, hash, file),
  getStatus: (repoPath) => ipcRenderer.invoke('git:getStatus', repoPath),
  stageFiles: (repoPath, files) => ipcRenderer.invoke('git:stageFiles', repoPath, files),
  unstageFiles: (repoPath, files) => ipcRenderer.invoke('git:unstageFiles', repoPath, files),
  commitChanges: (repoPath, message) => ipcRenderer.invoke('git:commitChanges', repoPath, message),
  getLiveDiff: (repoPath, file, isStaged) => ipcRenderer.invoke('git:getLiveDiff', repoPath, file, isStaged),
  fetchRepository: (repoPath) => ipcRenderer.invoke('git:fetch', repoPath),
  pullRepository: (repoPath) => ipcRenderer.invoke('git:pull', repoPath),
  pushRepository: (repoPath) => ipcRenderer.invoke('git:push', repoPath),
  getRemoteUrl: (repoPath) => ipcRenderer.invoke('git:getRemoteUrl', repoPath),
  openExternal: (url) => ipcRenderer.invoke('app:openExternal', url),
  onOpenRepo: (callback) => ipcRenderer.on('app:openRepo', (_event, value) => callback(value)),
  watchRepo: (repoPath) => ipcRenderer.send('app:watchRepo', repoPath),
  unwatchRepo: (repoPath) => ipcRenderer.send('app:unwatchRepo', repoPath),
  onRepoChanged: (callback) => ipcRenderer.on('repo:changed', (_event, value) => callback(value))
});
