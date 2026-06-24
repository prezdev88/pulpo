const { ipcRenderer } = require('electron');

const logContainer = document.getElementById('log-container');

function createLogElement(entry) {
    const div = document.createElement('div');
    div.className = 'log-entry';
    
    let outputHtml = '';
    if (entry.stderr && entry.stderr.trim() !== '') {
        outputHtml += `<div class="log-output" style="color: #fbbf24;">STDERR:\n${entry.stderr}</div>`;
    }
    if (entry.error) {
        outputHtml += `<div class="log-error">ERROR: ${entry.error}</div>`;
    }
    
    div.innerHTML = `
        <div class="log-header">
            <span>${new Date(entry.timestamp).toLocaleTimeString()} - ${entry.cwd}</span>
            <button class="clear-btn copy-cmd-btn" style="padding: 0.1rem 0.5rem; font-size: 0.75rem;" title="Copy to clipboard">Copy</button>
        </div>
        <div class="log-command">$ ${entry.command}</div>
        ${outputHtml}
    `;

    const copyBtn = div.querySelector('.copy-cmd-btn');
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(entry.command).then(() => {
            copyBtn.textContent = 'Copied!';
            setTimeout(() => copyBtn.textContent = 'Copy', 2000);
        });
    });

    return div;
}

function renderLogs(logs) {
    logContainer.innerHTML = '';
    if (logs.length === 0) {
        logContainer.innerHTML = '<div style="color: #888; text-align: center; margin-top: 2rem;">No logs yet.</div>';
        return;
    }
    logs.forEach(log => {
        logContainer.appendChild(createLogElement(log));
    });
    // Scroll to bottom
    logContainer.scrollTop = logContainer.scrollHeight;
}

// Initial load
ipcRenderer.invoke('git:getLogs').then(renderLogs);

// Listen for real-time updates
ipcRenderer.on('git:log', (event, logEntry) => {
    // If it was empty, clear the "No logs yet" message
    if (logContainer.querySelector('div[style]')) {
        logContainer.innerHTML = '';
    }
    logContainer.appendChild(createLogElement(logEntry));
    logContainer.scrollTop = logContainer.scrollHeight;
});

// Clear logs UI (only visually)
document.getElementById('clear-btn').addEventListener('click', () => {
    logContainer.innerHTML = '<div style="color: #888; text-align: center; margin-top: 2rem;">Logs cleared.</div>';
});
