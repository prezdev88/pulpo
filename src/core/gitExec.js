const { exec: originalExec } = require('child_process');
const { BrowserWindow } = require('electron');

// Store logs in memory
const logs = [];

function broadcastLog(logEntry) {
    logs.push(logEntry);
    // Send to all open windows (especially the log window)
    BrowserWindow.getAllWindows().forEach(win => {
        if (!win.isDestroyed()) {
            win.webContents.send('git:log', logEntry);
        }
    });
}

function exec(command, options, callback) {
    const timestamp = new Date().toISOString();
    
    // Handle overloaded arguments
    let actualOptions = typeof options === 'object' ? options : {};
    let actualCallback = typeof options === 'function' ? options : callback;

    return originalExec(command, actualOptions, (error, stdout, stderr) => {
        broadcastLog({
            timestamp,
            command,
            cwd: actualOptions.cwd || 'unknown',
            stdout: stdout ? stdout.toString() : '',
            stderr: stderr ? stderr.toString() : '',
            error: error ? error.message : null
        });
        
        if (actualCallback) {
            actualCallback(error, stdout, stderr);
        }
    });
}

module.exports = {
    exec,
    getLogs: () => logs
};
