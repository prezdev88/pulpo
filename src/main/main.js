const { app, BrowserWindow, ipcMain, Menu, shell } = require('electron');
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
const { getStatus } = require('../core/getStatusUseCase');
const { stageFiles } = require('../core/stageFilesUseCase');
const { unstageFiles } = require('../core/unstageFilesUseCase');
const { commitChanges } = require('../core/commitChangesUseCase');
const { getLiveDiff } = require('../core/getLiveDiffUseCase');
const { fetchUseCase } = require('../core/fetchUseCase');
const { pullUseCase } = require('../core/pullUseCase');
const { pushUseCase } = require('../core/pushUseCase');
const { getRemoteUrl } = require('../core/getRemoteUrlUseCase');
const gitExec = require('../core/gitExec');

let chokidar;
try {
  chokidar = require('chokidar');
} catch (e) {
  console.warn("Chokidar is not installed. File watching will be disabled.");
}

const activeWatchers = new Map();

let logWindow = null;

function openLogWindow() {
  if (logWindow) {
    logWindow.focus();
    return;
  }
  logWindow = new BrowserWindow({
    width: 800,
    height: 600,
    title: "Git Execution Logs",
    icon: path.join(__dirname, '../assets/logo.png'),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });
  logWindow.loadFile(path.join(__dirname, '../renderer/ui/git-logs.html'));
  logWindow.on('closed', () => {
    logWindow = null;
  });
}

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1024,
    height: 768,
    icon: path.join(__dirname, '../assets/logo.png'),
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
      label: 'Window',
      submenu: [
        {
          label: 'View Git Logs',
          click: openLogWindow
        }
      ]
    }
  ];
  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

app.whenReady().then(() => {
  ipcMain.handle('git:getLogs', () => {
    return gitExec.getLogs();
  });

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

  ipcMain.handle('git:getStatus', async (event, repoPath) => {
    return await getStatus(repoPath);
  });

  ipcMain.handle('git:stageFiles', async (event, repoPath, files) => {
    return await stageFiles(repoPath, files);
  });

  ipcMain.handle('git:unstageFiles', async (event, repoPath, files) => {
    return await unstageFiles(repoPath, files);
  });

  ipcMain.handle('git:commitChanges', async (event, repoPath, message) => {
    return await commitChanges(repoPath, message);
  });

  ipcMain.handle('git:getLiveDiff', async (event, repoPath, file, isStaged) => {
    return await getLiveDiff(repoPath, file, isStaged);
  });

  ipcMain.handle('git:fetch', async (event, repoPath) => {
    return await fetchUseCase(repoPath);
  });

  ipcMain.handle('git:pull', async (event, repoPath) => {
    return await pullUseCase(repoPath);
  });

  ipcMain.handle('git:push', async (event, repoPath) => {
    return await pushUseCase(repoPath);
  });

  ipcMain.handle('git:getRemoteUrl', async (event, repoPath) => {
    return await getRemoteUrl(repoPath);
  });

  ipcMain.handle('app:openExternal', async (event, url) => {
    return await shell.openExternal(url);
  });

  ipcMain.on('app:watchRepo', (event, repoPath) => {
    if (!chokidar) return;
    if (activeWatchers.has(repoPath)) return;
    
    const watcher = chokidar.watch(repoPath, {
      ignored: [
        '**/node_modules/**',
        '**/.git/objects/**',
        '**/.git/hooks/**',
        '**/.git/logs/**'
      ],
      persistent: true,
      ignoreInitial: true
    });

    let timeout;
    watcher.on('all', (eventName, filePath) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        BrowserWindow.getAllWindows().forEach(win => {
          win.webContents.send('repo:changed', repoPath);
        });
      }, 300);
    });

    activeWatchers.set(repoPath, watcher);
  });

  ipcMain.on('app:unwatchRepo', (event, repoPath) => {
    const watcher = activeWatchers.get(repoPath);
    if (watcher) {
      watcher.close();
      activeWatchers.delete(repoPath);
    }
  });

  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});
