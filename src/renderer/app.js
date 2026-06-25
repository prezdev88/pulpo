// Presentation logic, strictly separated from HTML/CSS

// DOM Elements
const landingView = document.getElementById('landing-card');
const commitsView = document.getElementById('commits-view');
const tabsBar = document.getElementById('tabs-bar');
const tabsContainer = document.getElementById('tabs-container');
const addTabBtn = document.getElementById('add-tab-btn');

// State
let tabState = {
    tabs: [],
    activeTabId: null
};
let activeRepoPath = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const openRepoBtn = document.getElementById('open-repo-btn');

    // Add Tab button
    addTabBtn.addEventListener('click', async () => {
        const repoPath = await window.api.selectRepository();
        if (repoPath) {
            openRepository(repoPath);
        }
    });

    if (openRepoBtn) {
        openRepoBtn.addEventListener('click', async () => {
            const repoPath = await window.api.selectRepository();
            if (repoPath) {
                openRepository(repoPath);
            }
        });
    }

    // Native menu integration
    if (window.api && window.api.onOpenRepo) {
        window.api.onOpenRepo((repoPath) => {
            openRepository(repoPath);
        });
    }

    // Delegación de eventos para las pestañas
    tabsContainer.addEventListener('click', (e) => {
        const tabEl = e.target.closest('.tab-item');
        if (!tabEl) return;
        const id = tabEl.dataset.id;
        
        if (e.target.classList.contains('tab-close')) {
            closeTab(id);
        } else {
            switchTab(id);
        }
    });

    async function loadRepoData(repoPath) {
        try {
            // Load branches
            const branchData = await window.api.getBranches(repoPath);
            const branchSelector = document.getElementById('branch-selector');
            branchSelector.innerHTML = '';
            branchData.branches.forEach(branch => {
                const option = document.createElement('option');
                option.value = branch;
                option.textContent = branch;
                if (branch === branchData.activeBranch) option.selected = true;
                branchSelector.appendChild(option);
            });

            // Load commits
            const commitsListEl = document.getElementById('commits-tbody');
            commitsListEl.innerHTML = '<li style="text-align: center; color: #888; padding: 2rem;">Loading commits...</li>';
            
            const commits = await window.api.getCommits(repoPath);
            renderCommits(commits, commitsListEl, repoPath);
        } catch (error) {
            console.error('Error loading repo data:', error);
            alert('Failed to load repository data.');
        }
    }

    // Old openRepoBtn listener removed to use the centralized openRepository function.

    const toggleBtn = document.getElementById('toggle-sidebar-btn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const sidebar = document.querySelector('.commits-sidebar');
            if (sidebar) sidebar.classList.toggle('hidden-sidebar');
            const resizerEl = document.getElementById('sidebar-resizer');
            if (resizerEl) resizerEl.classList.toggle('hidden-sidebar');
        });
    }

    // Sidebar Resizer Logic
    const sidebar = document.getElementById('commits-sidebar');
    const resizer = document.getElementById('sidebar-resizer');
    
    if (resizer && sidebar) {
        let isResizing = false;

        resizer.addEventListener('mousedown', (e) => {
            isResizing = true;
            resizer.classList.add('resizing');
            document.body.style.cursor = 'col-resize';
            e.preventDefault(); // Prevenir selección de texto
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;
            const newWidth = e.clientX;
            const maxWidth = window.innerWidth * 0.5; // Max 50vw
            
            if (newWidth >= 200 && newWidth <= maxWidth) {
                sidebar.style.width = `${newWidth}px`;
            }
        });

        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                resizer.classList.remove('resizing');
                document.body.style.cursor = '';
            }
        });
    }

    // Branch & Stash Controls
    document.getElementById('branch-selector').addEventListener('change', async (e) => {
        if (!activeRepoPath) return;
        try {
            await window.api.checkoutBranch(activeRepoPath, e.target.value);
            await loadRepoData(activeRepoPath);
        } catch (error) {
            alert('Error checking out branch:\n' + error.message);
            await loadRepoData(activeRepoPath);
        }
    });

    document.getElementById('new-branch-btn').addEventListener('click', () => {
        if (!activeRepoPath) return;
        const modal = document.getElementById('branch-modal');
        const input = document.getElementById('branch-name-input');
        input.value = '';
        modal.classList.remove('hidden');
        input.focus();
    });

    document.getElementById('cancel-branch-btn').addEventListener('click', () => {
        document.getElementById('branch-modal').classList.add('hidden');
    });

    document.getElementById('confirm-branch-btn').addEventListener('click', async () => {
        if (!activeRepoPath) return;
        const name = document.getElementById('branch-name-input').value.trim();
        if (name) {
            try {
                await window.api.createBranch(activeRepoPath, name);
                document.getElementById('branch-modal').classList.add('hidden');
                await loadRepoData(activeRepoPath);
            } catch (error) {
                alert('Error creating branch:\n' + error.message);
            }
        }
    });


    // Staging / Commit Controls

    document.getElementById('stage-all-btn').addEventListener('click', async () => {
        if (!activeRepoPath) return;
        try {
            await window.api.stageFiles(activeRepoPath, ['.']);
            loadStagingData(activeRepoPath);
        } catch(e) { alert(e.message); }
    });

    document.getElementById('unstage-all-btn').addEventListener('click', async () => {
        if (!activeRepoPath) return;
        try {
            await window.api.unstageFiles(activeRepoPath, ['.']);
            loadStagingData(activeRepoPath);
        } catch(e) { alert(e.message); }
    });

    document.getElementById('commit-message-input').addEventListener('input', (e) => {
        const tab = tabState.tabs.find(t => t.id === tabState.activeTabId);
        if (tab) {
            tab.commitMessage = e.target.value;
            saveTabsState();
        }
    });

    document.getElementById('commit-execute-btn').addEventListener('click', async () => {
        if (!activeRepoPath) return;
        const msg = document.getElementById('commit-message-input').value.trim();
        if (!msg) { alert('Please enter a commit message.'); return; }
        try {
            await window.api.commitChanges(activeRepoPath, msg);
            document.getElementById('commit-message-input').value = '';
            const tab = tabState.tabs.find(t => t.id === tabState.activeTabId);
            if (tab) tab.commitMessage = '';
            saveTabsState();
            loadStagingData(activeRepoPath);
            loadHistoryData(activeRepoPath);
        } catch(e) { alert(e.message); }
    });

    restoreTabsState();

    // Zoom on diff-viewer with Ctrl + MouseWheel
    const diffViewerEl = document.getElementById('diff-viewer');
    if (diffViewerEl) {
        let currentZoom = parseFloat(localStorage.getItem('pulpo-diff-zoom')) || 0.85;
        diffViewerEl.style.fontSize = `${currentZoom}rem`;

        diffViewerEl.addEventListener('wheel', (e) => {
            if (e.ctrlKey) {
                e.preventDefault();
                // Zoom in (scroll up) or Zoom out (scroll down)
                if (e.deltaY < 0) {
                    currentZoom += 0.05;
                } else {
                    currentZoom -= 0.05;
                }
                // Cap zoom levels
                currentZoom = Math.max(0.4, Math.min(currentZoom, 3.0));
                diffViewerEl.style.fontSize = `${currentZoom}rem`;
                localStorage.setItem('pulpo-diff-zoom', currentZoom.toString());
            }
        });
    }
});

// Funciones de Pestañas
function saveTabsState() {
    localStorage.setItem('pulpo-tabs', JSON.stringify(tabState.tabs));
    localStorage.setItem('pulpo-active-tab', tabState.activeTabId || '');
}

function restoreTabsState() {
    const savedTabs = localStorage.getItem('pulpo-tabs');
    const savedActiveId = localStorage.getItem('pulpo-active-tab');
    if (savedTabs) {
        try {
            tabState.tabs = JSON.parse(savedTabs);
            if (tabState.tabs.length > 0) {
                renderTabs();
                const tabToActivate = tabState.tabs.find(t => t.id === savedActiveId) || tabState.tabs[0];
                switchTab(tabToActivate.id);
            }
        } catch (e) {
            console.error('Error parsing tabs state', e);
        }
    }
}

function openRepository(repoPath) {
    const folderName = repoPath.split(/[\\/]/).pop();
    
    // Check if already open
    const existingTab = tabState.tabs.find(t => t.path === repoPath);
    if (existingTab) {
        switchTab(existingTab.id);
        return;
    }

    const id = Date.now().toString();
    tabState.tabs.push({ 
        id, 
        path: repoPath, 
        name: folderName,
        sidebarMode: 'history',
        commitMessage: ''
    });
    saveTabsState();
    switchTab(id);
}

function switchTab(id) {
    const tab = tabState.tabs.find(t => t.id === id);
    if (!tab) return;
    
    tabState.activeTabId = id;
    activeRepoPath = tab.path;
    document.getElementById('active-repo-name').textContent = tab.name;
    
    landingView.classList.add('hidden');
    tabsBar.classList.remove('hidden');
    commitsView.classList.remove('hidden');
    
    // Clear diff pane on tab switch
    document.getElementById('details-placeholder').classList.remove('hidden');
    document.getElementById('commit-details-content').classList.add('hidden');
    
    renderTabs();
    saveTabsState();
    
    // Apply saved message
    document.getElementById('commit-message-input').value = tab.commitMessage || '';
    
    // RNF03: Re-render when switching
    loadStagingData(tab.path);
    loadHistoryData(tab.path);
}

async function loadHistoryData(repoPath) {
    const commitsListEl = document.getElementById('commits-tbody');
    commitsListEl.innerHTML = '<li style="text-align: center; color: #888; padding: 2rem;">Loading commits...</li>';
    try {
        const branchData = await window.api.getBranches(repoPath);
        const branchSelector = document.getElementById('branch-selector');
        branchSelector.innerHTML = '';
        branchData.branches.forEach(branch => {
            const option = document.createElement('option');
            option.value = branch;
            option.textContent = branch;
            if (branch === branchData.activeBranch) option.selected = true;
            branchSelector.appendChild(option);
        });

        const commits = await window.api.getCommits(repoPath);
        renderCommits(commits, commitsListEl, repoPath);

        const tab = tabState.tabs.find(t => t.id === tabState.activeTabId);
        if (tab && tab.activeCommitHash && tab.activeFile && tab.activeCommitHash !== 'STAGED' && tab.activeCommitHash !== 'UNSTAGED') {
            const commitObj = commits.find(c => c.hash === tab.activeCommitHash);
            if (commitObj) {
                const commitRow = Array.from(commitsListEl.querySelectorAll('.commit-row')).find(row => row.querySelector('[data-field="hash"]').textContent === tab.activeCommitHash);
                if (commitRow) {
                    commitRow.classList.add('selected', 'expanded');
                    const inline = document.createElement('div');
                    inline.className = 'commit-files-inline';
                    inline.style.display = 'block';
                    commitRow.appendChild(inline);
                    
                    await loadCommitDetails(commitObj, repoPath, commitRow);
                    drawCommitGraph(commits, 'commit-graph-canvas');

                    const fileRow = Array.from(commitRow.querySelectorAll('.commit-file-row')).find(r => {
                        const pathParts = tab.activeFile.split('/');
                        return r.querySelector('.file-basename').textContent === pathParts[pathParts.length - 1];
                    });
                    if (fileRow) {
                        fileRow.classList.add('selected-file');
                    }
                    await loadFileDiff(repoPath, tab.activeCommitHash, tab.activeFile);
                }
            }
        }
    } catch (error) {
        console.error(error);
    }
}

// === STAGING LOGIC ===



async function loadStagingData(repoPath) {
    try {
        const status = await window.api.getStatus(repoPath);
        renderStagingFiles(status.staged, 'staged-files-list', true, repoPath);
        renderStagingFiles(status.unstaged, 'unstaged-files-list', false, repoPath);

        const tab = tabState.tabs.find(t => t.id === tabState.activeTabId);
        if (tab && tab.activeFile && (tab.activeCommitHash === 'STAGED' || tab.activeCommitHash === 'UNSTAGED')) {
            const isStaged = tab.activeCommitHash === 'STAGED';
            const listId = isStaged ? 'staged-files-list' : 'unstaged-files-list';
            const container = document.getElementById(listId);
            const fileRow = Array.from(container.querySelectorAll('li')).find(r => r.querySelector('.file-name').textContent === tab.activeFile);
            if (fileRow) {
                fileRow.classList.add('selected');
                await renderLiveDiff(repoPath, tab.activeFile, isStaged);
            }
        }
    } catch (err) {
        console.error('Error loading staging data:', err);
    }
}

function renderStagingFiles(files, containerId, isStaged, repoPath) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    if (files.length === 0) {
        container.innerHTML = '<li style="padding: 0.5rem 1rem; color: #666; font-size: 0.8rem;">No files</li>';
        return;
    }

    const template = document.getElementById('staging-file-template');
    
    files.forEach(f => {
        const clone = template.content.cloneNode(true);
        const li = clone.querySelector('li');
        
        clone.querySelector('.file-status').textContent = f.status;
        clone.querySelector('.file-name').textContent = f.file;
        
        const btn = clone.querySelector('.stage-toggle-btn');
        btn.innerHTML = isStaged ? '<i class="fa-solid fa-minus"></i>' : '<i class="fa-solid fa-plus"></i>';
        btn.title = isStaged ? 'Unstage' : 'Stage';
        
        btn.addEventListener('click', async (e) => {
            e.stopPropagation(); // Prevent opening diff
            try {
                if (isStaged) {
                    await window.api.unstageFiles(repoPath, [f.file]);
                } else {
                    await window.api.stageFiles(repoPath, [f.file]);
                }
                loadStagingData(repoPath);
            } catch (err) {
                alert(err.message);
            }
        });

        li.addEventListener('click', async () => {
            document.querySelectorAll('.staging-file-row').forEach(row => row.classList.remove('selected'));
            li.classList.add('selected');
            await renderLiveDiff(repoPath, f.file, isStaged);
        });

        container.appendChild(clone);
    });
}

async function renderLiveDiff(repoPath, file, isStaged) {
    document.getElementById('details-placeholder').classList.add('hidden');
    document.getElementById('commit-details-content').classList.remove('hidden');
    
    document.getElementById('detail-message').textContent = 'Live Changes';
    document.getElementById('detail-hash').textContent = isStaged ? 'Staged' : 'Unstaged';
    document.getElementById('detail-author').textContent = 'Working Directory';
    document.getElementById('detail-date').textContent = file;

    const diffViewerEl = document.getElementById('diff-viewer');
    document.getElementById('diff-file-list').innerHTML = `<div class="file-item" style="background:rgba(255,255,255,0.2)">${file}</div>`;
    diffViewerEl.innerHTML = '<div class="diff-placeholder">Loading diff...</div>';

    const tab = tabState.tabs.find(t => t.id === tabState.activeTabId);
    if (tab) {
        tab.activeCommitHash = isStaged ? 'STAGED' : 'UNSTAGED';
        tab.activeFile = file;
        saveTabsState();
    }

    try {
        const diffText = await window.api.getLiveDiff(repoPath, file, isStaged);
        diffViewerEl.innerHTML = '';
        
        if (!diffText) {
            diffViewerEl.innerHTML = '<div style="padding:1rem;">No visible diff (maybe binary or empty).</div>';
            return;
        }

        const lines = diffText.split('\n');
        lines.forEach(line => {
            const span = document.createElement('span');
            if (line.startsWith('+') && !line.startsWith('+++')) {
                span.className = 'diff-line-add';
            } else if (line.startsWith('-') && !line.startsWith('---')) {
                span.className = 'diff-line-del';
            } else if (line.startsWith('@@')) {
                span.className = 'diff-line-info';
            } else {
                span.className = 'diff-line-normal';
            }
            span.textContent = line + '\n';
            diffViewerEl.appendChild(span);
        });
    } catch (err) {
        diffViewerEl.innerHTML = `<div style="color:red;">Error: ${err.message}</div>`;
    }
}

function closeTab(id) {
    const index = tabState.tabs.findIndex(t => t.id === id);
    if (index === -1) return;
    
    tabState.tabs.splice(index, 1);
    
    if (tabState.tabs.length === 0) {
        tabState.activeTabId = null;
        activeRepoPath = null;
        tabsBar.classList.add('hidden');
        commitsView.classList.add('hidden');
        landingView.classList.remove('hidden');
    } else if (tabState.activeTabId === id) {
        const nextIndex = Math.max(0, index - 1);
        switchTab(tabState.tabs[nextIndex].id);
    } else {
        renderTabs();
    }
    saveTabsState();
}

function renderTabs() {
    tabsContainer.innerHTML = '';
    tabState.tabs.forEach(tab => {
        const div = document.createElement('div');
        div.className = `tab-item ${tab.id === tabState.activeTabId ? 'active' : ''}`;
        div.dataset.id = tab.id;
        div.title = tab.path; // Set the tooltip to the full path
        
        div.innerHTML = `
            <span class="tab-label">${tab.name}</span>
            <button class="tab-close">×</button>
        `;
        tabsContainer.appendChild(div);
    });
}

function renderCommits(commits, container, repoPath) {
    container.innerHTML = '';
    
    if (!commits || commits.length === 0) {
        container.innerHTML = '<li style="text-align: center; color: #888; padding: 2rem;">No commits found or not a valid Git repository.</li>';
        return;
    }

    const template = document.getElementById('commit-template');
    
    commits.forEach(commit => {
        // RNF05: Use template cloning to keep HTML/CSS decoupled from JS Logic
        const clone = template.content.cloneNode(true);
        const li = clone.querySelector('li');
        
        clone.querySelector('[data-field="hash"]').textContent = commit.hash;
        clone.querySelector('[data-field="date"]').textContent = commit.date;
        clone.querySelector('[data-field="message"]').textContent = commit.message;
        clone.querySelector('[data-field="author"]').textContent = commit.author;
        
        li.addEventListener('click', async () => {
            const isExpanded = li.classList.contains('expanded');
            
            // Mark as selected for the top panel
            document.querySelectorAll('.commit-row').forEach(row => {
                row.classList.remove('selected');
            });
            li.classList.add('selected');

            if (isExpanded) {
                // Close it
                li.classList.remove('expanded');
                const inline = li.querySelector('.commit-files-inline');
                if (inline) {
                    inline.innerHTML = '';
                    inline.style.display = 'none';
                }
                drawCommitGraph(commits, 'commit-graph-canvas');
            } else {
                // Open it
                li.classList.add('expanded');
                const inline = li.querySelector('.commit-files-inline') || document.createElement('div');
                inline.className = 'commit-files-inline';
                inline.style.display = 'block';
                li.appendChild(inline);
                
                await loadCommitDetails(commit, repoPath, li);
                drawCommitGraph(commits, 'commit-graph-canvas');
            }
        });

        container.appendChild(clone);
    });

    // RNF05 & T06: Draw Visual Commit Graph
    setTimeout(() => {
        drawCommitGraph(commits, 'commit-graph-canvas');
    }, 0);
}

function drawCommitGraph(commits, canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const rows = document.querySelectorAll('.commit-row');
    if (rows.length === 0) return;

    const rowHeight = rows[0].offsetHeight || 48;
    const totalHeight = rows[rows.length - 1].offsetTop + rowHeight;
    const width = 60;
    
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = totalHeight * dpr;
    canvas.style.width = width + 'px';
    canvas.style.height = totalHeight + 'px';

    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, width, totalHeight);

    const tracks = [];
    const commitCoords = {};
    const colors = ['#bb86fc', '#03dac6', '#cf6679', '#ffb74d', '#64b5f6', '#81c784'];

    commits.forEach((commit, i) => {
        let trackIndex = tracks.findIndex(t => t === commit.hash);
        
        if (trackIndex === -1) {
            trackIndex = tracks.findIndex(t => !t);
            if (trackIndex === -1) {
                trackIndex = tracks.length;
                tracks.push(commit.hash);
            } else {
                tracks[trackIndex] = commit.hash;
            }
        }

        const x = 20 + (trackIndex * 10);
        const y = rows[i].offsetTop + (rowHeight / 2);
        const color = colors[trackIndex % colors.length];
        
        commitCoords[commit.hash] = { x, y, color };

        if (commit.parents && commit.parents.length > 0) {
            tracks[trackIndex] = commit.parents[0];
            for (let p = 1; p < commit.parents.length; p++) {
                const parentHash = commit.parents[p];
                const emptyIdx = tracks.findIndex(t => !t);
                if (emptyIdx === -1) {
                    tracks.push(parentHash);
                } else {
                    tracks[emptyIdx] = parentHash;
                }
            }
        } else {
            tracks[trackIndex] = null;
        }
    });

    ctx.lineWidth = 2;
    commits.forEach(commit => {
        const start = commitCoords[commit.hash];
        if (!start || !commit.parents) return;

        commit.parents.forEach((parentHash, idx) => {
            const end = commitCoords[parentHash];
            if (end) {
                ctx.beginPath();
                ctx.moveTo(start.x, start.y);
                ctx.bezierCurveTo(
                    start.x, start.y + rowHeight / 2,
                    end.x, end.y - rowHeight / 2,
                    end.x, end.y
                );
                ctx.strokeStyle = idx === 0 ? start.color : end.color;
                ctx.stroke();
            }
        });
    });

    commits.forEach(commit => {
        const coord = commitCoords[commit.hash];
        if (!coord) return;

        ctx.beginPath();
        ctx.arc(coord.x, coord.y, 4, 0, 2 * Math.PI);
        ctx.fillStyle = coord.color;
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#1e1e1e';
        ctx.stroke();
    });
}

async function loadCommitDetails(commit, repoPath, commitLi) {
    document.getElementById('details-placeholder').classList.add('hidden');
    document.getElementById('commit-details-content').classList.remove('hidden');

    document.getElementById('detail-message').textContent = commit.message;
    document.getElementById('detail-hash').textContent = commit.hash;
    document.getElementById('detail-author').textContent = commit.author;
    document.getElementById('detail-date').textContent = commit.date;

    const diffViewerEl = document.getElementById('diff-viewer');
    diffViewerEl.innerHTML = '<div class="diff-placeholder">Select a file to view its diff</div>';

    let inlineContainer = commitLi.querySelector('.commit-files-inline');
    if (!inlineContainer) {
        inlineContainer = document.createElement('div');
        inlineContainer.className = 'commit-files-inline';
        commitLi.appendChild(inlineContainer);
    }

    inlineContainer.innerHTML = '<div style="padding:0.5rem;color:#888;">Loading files...</div>';

    try {
        const files = await window.api.getCommitFiles(repoPath, commit.hash);
        inlineContainer.innerHTML = '';
        
        if (files.length === 0) {
            inlineContainer.innerHTML = '<div style="padding:0.5rem;color:#888;">No files changed.</div>';
            return;
        }

        files.forEach(f => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item commit-file-row';
            
            const pathParts = f.file.split('/');
            const basename = pathParts.pop();
            const directory = pathParts.join('/') || '.';

            let icon = '<i class="fa-solid fa-file"></i>';
            if (basename.endsWith('.md')) icon = '<i class="fa-solid fa-file-lines"></i>';
            else if (basename.endsWith('.js') || basename.endsWith('.ts')) icon = '<i class="fa-brands fa-js"></i>';
            else if (basename.endsWith('.json')) icon = '<i class="fa-solid fa-file-code"></i>';
            else if (basename.endsWith('.css') || basename.endsWith('.html')) icon = '<i class="fa-brands fa-html5"></i>';

            fileItem.innerHTML = `
                <span class="file-icon">${icon}</span>
                <span class="file-basename">${basename}</span>
                <span class="file-directory">${directory}</span>
                <span class="file-status-indicator status-${f.status}">${f.status}</span>
            `;

            fileItem.addEventListener('click', async (e) => {
                e.stopPropagation(); // Prevent closing the commit row
                document.querySelectorAll('.file-item').forEach(el => el.classList.remove('selected-file'));
                fileItem.classList.add('selected-file');
                await loadFileDiff(repoPath, commit.hash, f.file);
            });
            inlineContainer.appendChild(fileItem);
        });
    } catch (err) {
        inlineContainer.innerHTML = `<div style="color:red;">Error: ${err.message}</div>`;
    }
}

async function loadFileDiff(repoPath, hash, file) {
    const diffViewerEl = document.getElementById('diff-viewer');
    diffViewerEl.innerHTML = '<div class="diff-placeholder">Loading diff...</div>';

    try {
        const diffText = await window.api.getFileDiff(repoPath, hash, file);
        diffViewerEl.innerHTML = '';
        
        let oldLineNum = 0;
        let newLineNum = 0;

        const lines = diffText.split('\n');
        lines.forEach(line => {
            if (line.startsWith('@@ ')) {
                // Parse @@ -oldStart,oldCount +newStart,newCount @@
                const match = line.match(/@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@/);
                if (match) {
                    oldLineNum = parseInt(match[1], 10);
                    newLineNum = parseInt(match[2], 10);
                }
                return; // skip rendering the @@ line itself
            }

            // Skip metadata lines to show only code
            if (line.startsWith('diff --git') ||
                line.startsWith('index ') ||
                line.match(/^(new|deleted) file mode /) ||
                line.startsWith('--- ') ||
                line.startsWith('+++ ') ||
                line.startsWith('\\ No newline')) {
                return;
            }

            let oldNumStr = '';
            let newNumStr = '';

            const row = document.createElement('div');
            if (line.startsWith('+')) {
                row.className = 'diff-line-add';
                newNumStr = newLineNum++;
            } else if (line.startsWith('-')) {
                row.className = 'diff-line-del';
                oldNumStr = oldLineNum++;
            } else {
                row.className = 'diff-line-normal';
                oldNumStr = oldLineNum++;
                newNumStr = newLineNum++;
            }

            // Escape HTML tags in the code content
            const safeContent = line.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

            row.innerHTML = `
                <div class="diff-gutters">
                    <span class="diff-line-num">${oldNumStr}</span>
                    <span class="diff-line-num">${newNumStr}</span>
                </div>
                <span class="diff-line-content">${safeContent}</span>
            `;
            diffViewerEl.appendChild(row);
        });

        const tab = tabState.tabs.find(t => t.id === tabState.activeTabId);
        if (tab) {
            tab.activeCommitHash = hash;
            tab.activeFile = file;
            saveTabsState();
        }
    } catch (err) {
        diffViewerEl.innerHTML = `<div style="color:red;">Error: ${err.message}</div>`;
    }
}
