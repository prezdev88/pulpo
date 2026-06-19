const { app, BrowserWindow, ipcMain, Menu } = require('electron');
const path = require('path');
const { selectRepository } = require('../core/selectRepositoryUseCase');
const { getCommits } = require('../core/getCommitsUseCase');
const getBranches = require('../core/getBranchesUseCase');
const checkoutBranch = require('../core/checkoutBranchUseCase');
const createBranch = require('../core/createBranchUseCase');
const stashChanges = require('../core/stashChangesUseCase');
const popStash = require('../core/popStashUseCase');
const getCommitFiles = require('../core/getCommitFilesUseCase');
const getFileDiff = require('../core/getFileDiffUseCase');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1024,
    height: 768,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.loadFile(path.join(__dirname, '../renderer/ui/index.html'));

  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Open Repository...',
          accelerator: 'CmdOrCtrl+O',
          click: async () => {
            const repoPath = await selectRepository();
            if (repoPath) {
              mainWindow.webContents.send('app:openRepo', repoPath);
            }
          }
        },
        { type: 'separator' },
        { role: 'quit' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'toggleDevTools' }
      ]
    }
  ];
  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

app.whenReady().then(() => {
  ipcMain.handle('dialog:openDirectory', async () => {
    return await selectRepository();
  });

  ipcMain.handle('git:getCommits', async (event, repoPath) => {
    return await getCommits(repoPath);
  });

  ipcMain.handle('git:getBranches', async (event, repoPath) => {
    return await getBranches(repoPath);
  });

  ipcMain.handle('git:checkout', async (event, repoPath, branchName) => {
    return await checkoutBranch(repoPath, branchName);
  });

  ipcMain.handle('git:createBranch', async (event, repoPath, branchName) => {
    return await createBranch(repoPath, branchName);
  });

  ipcMain.handle('git:stash', async (event, repoPath) => {
    return await stashChanges(repoPath);
  });

  ipcMain.handle('git:stashPop', async (event, repoPath) => {
    return await popStash(repoPath);
  });

  ipcMain.handle('git:getCommitFiles', async (event, repoPath, hash) => {
    return await getCommitFiles(repoPath, hash);
  });

  ipcMain.handle('git:getFileDiff', async (event, repoPath, hash, file) => {
    return await getFileDiff(repoPath, hash, file);
  });

  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});
