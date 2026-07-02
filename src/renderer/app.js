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
let monacoEditorInstance = null;
let currentBranchTargetCommit = null;
// Toast Function
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message.trim();

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

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

    document.addEventListener('click', () => {
        const ctxMenu = document.getElementById('commit-context-menu');
        if (ctxMenu) ctxMenu.classList.add('hidden');
    });

    const ctxCreateBranch = document.getElementById('ctx-create-branch');
    if (ctxCreateBranch) {
        ctxCreateBranch.addEventListener('click', () => {
            const modal = document.getElementById('branch-modal');
            const input = document.getElementById('branch-name-input');
            input.value = '';
            modal.classList.remove('hidden');
            input.focus();
        });
    }

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

    // Remote URL Link click
    const remoteLink = document.getElementById('remote-url-display');
    if (remoteLink) {
        remoteLink.addEventListener('click', async (e) => {
            e.preventDefault();
            const url = e.target.dataset.webUrl;
            if (url && window.api && window.api.openExternal) {
                await window.api.openExternal(url);
            }
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

            // Load remote URL
            const remoteUrl = await window.api.getRemoteUrl(repoPath);
            const remoteDisplay = document.getElementById('remote-url-display');
            if (remoteDisplay) {
                remoteDisplay.textContent = remoteUrl || 'No remote configured';
            }
        } catch (error) {
            console.error('Error loading repo data:', error);
            alert('Failed to load repository data.');
        }
    }

    // Old openRepoBtn listener removed to use the centralized openRepository function.



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

    // Commits Panel Resizer Logic
    const commitsPanel = document.getElementById('commits-panel');
    const hResizer = document.getElementById('commits-resizer');
    
    if (hResizer && commitsPanel) {
        let isHResizing = false;
        
        hResizer.addEventListener('mousedown', (e) => {
            if (commitsPanel.classList.contains('collapsed-panel')) return;
            isHResizing = true;
            hResizer.classList.add('resizing');
            commitsPanel.style.transition = 'none'; // Prevent lag during resize
            document.body.style.cursor = 'row-resize';
            e.preventDefault();
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isHResizing) return;
            const sidebar = document.querySelector('.commits-sidebar');
            const sidebarRect = sidebar.getBoundingClientRect();
            let newHeight = sidebarRect.bottom - e.clientY;
            
            const minHeight = 100;
            // Reservar al menos 220px para el repo header, textarea de commit y titulos de staging
            const maxHeight = Math.max(minHeight, sidebarRect.height - 220);
            
            if (newHeight < minHeight) newHeight = minHeight;
            if (newHeight > maxHeight) newHeight = maxHeight;
            
            commitsPanel.style.height = `${newHeight}px`;
        });
        
        document.addEventListener('mouseup', () => {
            if (isHResizing) {
                isHResizing = false;
                hResizer.classList.remove('resizing');
                commitsPanel.style.transition = ''; // Restore transition
                document.body.style.cursor = '';
            }
        });
    }

    // Network Controls
    document.getElementById('fetch-btn').addEventListener('click', async () => {
        if (!activeRepoPath) return;
        try {
            document.getElementById('fetch-btn').style.opacity = '0.5';
            const output = await window.api.fetchRepository(activeRepoPath);
            showToast(output, 'success');
            await loadRepoData(activeRepoPath);
        } catch (error) {
            showToast('Error fetching:\n' + error.message, 'error');
        } finally {
            document.getElementById('fetch-btn').style.opacity = '1';
        }
    });

    document.getElementById('pull-btn').addEventListener('click', async () => {
        if (!activeRepoPath) return;
        try {
            document.getElementById('pull-btn').style.opacity = '0.5';
            const output = await window.api.pullRepository(activeRepoPath);
            showToast(output, 'success');
            await loadRepoData(activeRepoPath);
            loadStagingData(activeRepoPath);
        } catch (error) {
            showToast('Error pulling:\n' + error.message, 'error');
        } finally {
            document.getElementById('pull-btn').style.opacity = '1';
        }
    });

    document.getElementById('push-btn').addEventListener('click', async () => {
        if (!activeRepoPath) return;
        try {
            document.getElementById('push-btn').style.opacity = '0.5';
            const output = await window.api.pushRepository(activeRepoPath);
            showToast(output, 'success');
            await loadRepoData(activeRepoPath);
        } catch (error) {
            showToast('Error pushing:\n' + error.message, 'error');
        } finally {
            document.getElementById('push-btn').style.opacity = '1';
        }
    });

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
        currentBranchTargetCommit = null;
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
                await window.api.createBranch(activeRepoPath, name, currentBranchTargetCommit);
                document.getElementById('branch-modal').classList.add('hidden');
                await loadRepoData(activeRepoPath);
            } catch (error) {
                alert('Error creating branch:\n' + error.message);
            }
        }
    });

    document.getElementById('delete-branch-btn').addEventListener('click', () => {
        if (!activeRepoPath) return;
        const branchSelector = document.getElementById('branch-selector');
        const currentBranch = branchSelector.value;
        if (!currentBranch) return;
        
        const modal = document.getElementById('delete-branch-modal');
        document.getElementById('delete-branch-text').textContent = `Are you sure you want to delete the branch '${currentBranch}'?`;
        modal.classList.remove('hidden');
    });

    document.getElementById('cancel-delete-branch-btn').addEventListener('click', () => {
        document.getElementById('delete-branch-modal').classList.add('hidden');
    });

    document.getElementById('confirm-delete-branch-btn').addEventListener('click', async () => {
        if (!activeRepoPath) return;
        const branchSelector = document.getElementById('branch-selector');
        const branchToDelete = branchSelector.value;
        if (!branchToDelete) return;

        try {
            // Determine principal branch
            const branchData = await window.api.getBranches(activeRepoPath);
            let principalBranch = branchData.branches.includes('main') ? 'main' : (branchData.branches.includes('master') ? 'master' : null);
            
            // If main/master doesn't exist, pick the first available branch that isn't the one we are deleting
            if (!principalBranch) {
                principalBranch = branchData.branches.find(b => b !== branchToDelete);
            }

            // Checkout to principal branch first (unless we are trying to delete the only branch)
            if (principalBranch && principalBranch !== branchToDelete) {
                await window.api.checkoutBranch(activeRepoPath, principalBranch);
            }

            await window.api.deleteBranch(activeRepoPath, branchToDelete);
            document.getElementById('delete-branch-modal').classList.add('hidden');
            showToast(`Branch '${branchToDelete}' deleted successfully. Switched to '${principalBranch}'.`, 'success');
            await loadRepoData(activeRepoPath);
        } catch (error) {
            document.getElementById('delete-branch-modal').classList.add('hidden');
            alert('Error deleting branch:\n' + error.message);
        }
    });


    // Accordion Toggle Logic
    document.querySelectorAll('.accordion-header').forEach(header => {
        header.addEventListener('click', (e) => {
            if (e.target.closest('.accordion-actions')) return;
            header.classList.toggle('collapsed');
            const content = header.nextElementSibling;
            if (content && content.classList.contains('accordion-content')) {
                content.classList.toggle('collapsed');
            }
            if (header.parentElement.id === 'commits-panel') {
                if (header.classList.contains('collapsed')) {
                    header.parentElement.dataset.prevHeight = header.parentElement.getBoundingClientRect().height + 'px';
                    header.parentElement.style.height = header.getBoundingClientRect().height + 'px';
                    header.parentElement.classList.add('collapsed-panel');
                } else {
                    header.parentElement.style.height = header.parentElement.dataset.prevHeight || '300px';
                    header.parentElement.classList.remove('collapsed-panel');
                }
            }
        });
    });

    // Staging / Commit Controls

    document.getElementById('discard-all-btn').addEventListener('click', async () => {
        if (!activeRepoPath) return;
        if (!confirm('Are you sure you want to discard ALL unstaged changes? This cannot be undone.')) return;
        try {
            await window.api.discardChanges(activeRepoPath, ['.']);
            loadStagingData(activeRepoPath);
        } catch(e) { alert('Error discarding changes: ' + e.message); }
    });

    document.getElementById('stage-all-btn').addEventListener('click', async () => {
        if (!activeRepoPath) return;
        try {
            await window.api.stageFiles(activeRepoPath, ['.']);
            loadStagingData(activeRepoPath);
        } catch(e) { alert(e.message); }
    });

    document.getElementById('discard-all-staged-btn').addEventListener('click', async () => {
        if (!activeRepoPath) return;
        if (!confirm('Are you sure you want to discard ALL staged changes? This cannot be undone.')) return;
        try {
            // Get all staged files from the UI list
            const stagedList = document.getElementById('staged-files-list');
            const fileRows = Array.from(stagedList.querySelectorAll('li'));
            const filesToDiscard = fileRows.map(li => {
                const basename = li.querySelector('.file-name').textContent;
                const dir = li.querySelector('.file-directory').textContent;
                return dir ? `${dir}/${basename}` : basename;
            });
            if (filesToDiscard.length === 0) return;

            await window.api.discardChanges(activeRepoPath, filesToDiscard);
            loadStagingData(activeRepoPath);
        } catch(e) { alert('Error discarding staged changes: ' + e.message); }
    });

    document.getElementById('unstage-all-btn').addEventListener('click', async () => {
        if (!activeRepoPath) return;
        try {
            await window.api.unstageFiles(activeRepoPath, ['.']);
            loadStagingData(activeRepoPath);
        } catch(e) { alert(e.message); }
    });

    // Stash Buttons
    const stashChangesBtn = document.getElementById('stash-changes-btn');
    if (stashChangesBtn) {
        stashChangesBtn.addEventListener('click', () => {
            if (!activeRepoPath) return;
            const modal = document.getElementById('stash-modal');
            const input = document.getElementById('stash-message-input');
            input.value = '';
            modal.classList.remove('hidden');
            input.focus();
        });
    }

    const cancelStashBtn = document.getElementById('cancel-stash-btn');
    if (cancelStashBtn) {
        cancelStashBtn.addEventListener('click', () => {
            document.getElementById('stash-modal').classList.add('hidden');
        });
    }

    const confirmStashBtn = document.getElementById('confirm-stash-btn');
    if (confirmStashBtn) {
        confirmStashBtn.addEventListener('click', async () => {
            if (!activeRepoPath) return;
            const msg = document.getElementById('stash-message-input').value.trim();
            try {
                confirmStashBtn.disabled = true;
                await window.api.stashChanges(activeRepoPath, msg);
                document.getElementById('stash-modal').classList.add('hidden');
                showToast('Changes stashed successfully.', 'success');
                loadStagingData(activeRepoPath);
            } catch (error) {
                alert('Error stashing changes:\n' + error.message);
            } finally {
                confirmStashBtn.disabled = false;
            }
        });
    }

    document.getElementById('commit-message-input').addEventListener('input', (e) => {
        const tab = tabState.tabs.find(t => t.id === tabState.activeTabId);
        if (tab) {
            tab.commitMessage = e.target.value;
            saveTabsState();
        }
    });

    const executeBtn = document.getElementById('commit-execute-btn');
    executeBtn.addEventListener('click', async () => {
        if (!activeRepoPath) return;
        const action = executeBtn.getAttribute('data-action');
        const originalText = executeBtn.textContent;
        
        if (action === 'push') {
            try {
                executeBtn.disabled = true;
                executeBtn.textContent = 'Pushing...';
                showToast('Pushing to remote...', 'info');
                await window.api.pushRepository(activeRepoPath);
                showToast('Push successful!', 'success');
                loadStagingData(activeRepoPath);
                loadHistoryData(activeRepoPath);
            } catch(e) {
                executeBtn.disabled = false;
                executeBtn.textContent = originalText;
                alert(e.message);
            }
            return;
        }

        // Action is 'commit'
        const msg = document.getElementById('commit-message-input').value.trim();
        if (!msg) { alert('Please enter a commit message.'); return; }
        try {
            executeBtn.disabled = true;
            executeBtn.textContent = 'Committing...';
            await window.api.commitChanges(activeRepoPath, msg);
            document.getElementById('commit-message-input').value = '';
            const tab = tabState.tabs.find(t => t.id === tabState.activeTabId);
            if (tab) tab.commitMessage = '';
            saveTabsState();
            loadStagingData(activeRepoPath);
            loadHistoryData(activeRepoPath);
        } catch(e) { 
            executeBtn.disabled = false;
            executeBtn.textContent = originalText;
            alert(e.message); 
        }
    });

    restoreTabsState();

    // Custom fast zoom and persistence for Monaco Editor
    const diffViewerEl = document.getElementById('diff-viewer');
    if (diffViewerEl) {
        diffViewerEl.addEventListener('wheel', (e) => {
            if (e.ctrlKey) {
                e.preventDefault();
                e.stopPropagation();
                let currentFontSize = parseInt(localStorage.getItem('pulpo-monaco-fontsize')) || 14;
                if (e.deltaY < 0) {
                    currentFontSize += 2; // Zoom in fast
                } else {
                    currentFontSize -= 2; // Zoom out fast
                }
                currentFontSize = Math.max(8, Math.min(currentFontSize, 40));
                localStorage.setItem('pulpo-monaco-fontsize', currentFontSize.toString());
                
                if (monacoEditorInstance) {
                    monacoEditorInstance.updateOptions({ fontSize: currentFontSize });
                }
            }
        }, { capture: true, passive: false });
    }

    if (window.api && window.api.onRepoChanged) {
        let repoUpdateTimeout;
        window.api.onRepoChanged((repoPath) => {
            if (activeRepoPath === repoPath) {
                clearTimeout(repoUpdateTimeout);
                repoUpdateTimeout = setTimeout(() => {
                    console.log('Real-time file change detected in', repoPath);
                    loadStagingData(repoPath);
                    loadHistoryData(repoPath); 
                }, 1500);
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
    // Repository name heading was removed
    
    landingView.classList.add('hidden');
    tabsBar.classList.remove('hidden');
    commitsView.classList.remove('hidden');
    document.getElementById('status-bar').classList.remove('hidden');
    
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

    if (window.api && window.api.watchRepo) {
        window.api.watchRepo(tab.path);
    }
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

        // Load remote URL
        const remoteUrl = await window.api.getRemoteUrl(repoPath);
        const remoteDisplay = document.getElementById('remote-url-display');
        if (remoteDisplay) {
            if (remoteUrl) {
                remoteDisplay.textContent = remoteUrl;
                remoteDisplay.classList.remove('disabled');
                
                // Format to web URL
                let webUrl = remoteUrl;
                if (webUrl.startsWith('git@')) {
                    webUrl = 'https://' + webUrl.substring(4).replace(':', '/').replace(/\.git$/, '');
                } else if (webUrl.startsWith('http')) {
                    webUrl = webUrl.replace(/\.git$/, '');
                }
                remoteDisplay.dataset.webUrl = webUrl;
            } else {
                remoteDisplay.textContent = 'No remote configured';
                remoteDisplay.classList.add('disabled');
                remoteDisplay.dataset.webUrl = '';
            }
        }

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
        
        document.getElementById('staged-count').textContent = status.staged.length;
        document.getElementById('changes-count').textContent = status.unstaged.length;

        renderStagingFiles(status.staged, 'staged-files-list', true, repoPath);
        renderStagingFiles(status.unstaged, 'unstaged-files-list', false, repoPath);
        
        // Handle Stash Button State
        const stashBtn = document.getElementById('stash-changes-btn');
        if (stashBtn) {
            const hasChanges = status.unstaged.length > 0 || status.staged.length > 0;
            stashBtn.disabled = !hasChanges;
            stashBtn.style.opacity = hasChanges ? '1' : '0.3';
            stashBtn.style.cursor = hasChanges ? 'pointer' : 'not-allowed';
        }
        
        if(typeof loadStashesData === 'function') loadStashesData(repoPath);

        const tab = tabState.tabs.find(t => t.id === tabState.activeTabId);
        
        const container = document.getElementById('unified-view-container');
        const changesAcc = document.getElementById('changes-accordion');
        const stagedAcc = document.getElementById('staged-accordion');
        const commitBtn = document.getElementById('commit-execute-btn');
        if (container && changesAcc && stagedAcc) {
            if (status.staged.length === 0) {
                stagedAcc.classList.add('hidden');
                if (commitBtn) {
                    if (status.ahead > 0) {
                        commitBtn.textContent = `Push (${status.ahead})`;
                        commitBtn.setAttribute('data-action', 'push');
                        commitBtn.disabled = false;
                    } else {
                        commitBtn.textContent = 'Commit';
                        commitBtn.setAttribute('data-action', 'commit');
                        commitBtn.disabled = true;
                    }
                }
            } else {
                stagedAcc.classList.remove('hidden');
                container.insertBefore(stagedAcc, changesAcc);
                if (commitBtn) {
                    commitBtn.textContent = 'Commit';
                    commitBtn.setAttribute('data-action', 'commit');
                    commitBtn.disabled = false;
                }
            }
        }

        if (tab && tab.activeFile && (tab.activeCommitHash === 'STAGED' || tab.activeCommitHash === 'UNSTAGED')) {
            const isStaged = tab.activeCommitHash === 'STAGED';
            const listId = isStaged ? 'staged-files-list' : 'unstaged-files-list';
            const listContainer = document.getElementById(listId);
            const fileRow = Array.from(listContainer.querySelectorAll('li')).find(r => r.querySelector('.file-name').textContent === tab.activeFile.split('/').pop());
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
        
        const pathParts = f.file.split('/');
        const basename = pathParts.pop();
        const directory = pathParts.length > 0 ? pathParts.join('/') : '';
        
        let iconHtml = '<i class="fa-solid fa-file" style="color: #ccc;"></i>';
        if (basename.endsWith('.md')) iconHtml = '<i class="fa-solid fa-file-lines" style="color: #69b4d9;"></i>';
        else if (basename.endsWith('.js') || basename.endsWith('.ts')) iconHtml = '<i class="fa-brands fa-js" style="color: #f1e05a;"></i>';
        else if (basename.endsWith('.json')) iconHtml = '<i class="fa-solid fa-file-code" style="color: #854CC7;"></i>';
        else if (basename.endsWith('.css') || basename.endsWith('.html')) iconHtml = '<i class="fa-brands fa-html5" style="color: #e34c26;"></i>';

        clone.querySelector('.file-icon').innerHTML = iconHtml;
        clone.querySelector('.file-name').textContent = basename;
        clone.querySelector('.file-directory').textContent = directory;
        
        const statusSpan = clone.querySelector('.file-status');
        let shortStatus = f.status.charAt(0).toUpperCase();
        if (f.status.includes('?')) shortStatus = 'U';
        statusSpan.textContent = shortStatus;
        
        if (shortStatus === 'M') statusSpan.style.color = '#e2c08d';
        else if (shortStatus === 'A' || shortStatus === 'U') statusSpan.style.color = '#73c991';
        else if (shortStatus === 'D') statusSpan.style.color = '#f14c4c';
        else statusSpan.style.color = '#888';
        
        const btn = clone.querySelector('.stage-toggle-btn');
        btn.innerHTML = isStaged ? '<i class="fa-solid fa-minus"></i>' : '<i class="fa-solid fa-plus"></i>';
        btn.title = isStaged ? 'Unstage' : 'Stage';
        
        const discardBtn = clone.querySelector('.discard-file-btn');
        discardBtn.style.display = 'inline-flex';
        discardBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            if (!confirm(`Are you sure you want to discard changes in ${f.file}?`)) return;
            try {
                await window.api.discardChanges(repoPath, [f.file]);
                loadStagingData(repoPath);
            } catch (err) {
                alert('Error discarding changes: ' + err.message);
            }
        });

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
            tabState.tabs.find(t => t.id === tabState.activeTabId).activeFile = f.file;
            await renderLiveDiff(repoPath, f.file, isStaged);
        });

        container.appendChild(clone);
    });
}

async function loadStashesData(repoPath) {
    try {
        const stashes = await window.api.listStashes(repoPath);
        const countBadge = document.getElementById('stashes-count');
        if (countBadge) countBadge.textContent = stashes.length;
        
        const container = document.getElementById('stashes-list');
        if (!container) return;
        container.innerHTML = '';
        
        const stashesAcc = document.getElementById('stashes-accordion');
        if (stashes.length === 0) {
            if (stashesAcc) stashesAcc.classList.add('hidden');
            return;
        } else {
            if (stashesAcc) stashesAcc.classList.remove('hidden');
        }

        const template = document.getElementById('stash-row-template');
        if (!template) return;
        
        stashes.forEach(stash => {
            const clone = template.content.cloneNode(true);
            const li = clone.querySelector('li');
            
            clone.querySelector('.stash-message').textContent = stash.message;
            clone.querySelector('.stash-meta').textContent = `${stash.id} • ${stash.date}`;
            
            const actions = clone.querySelector('.stash-actions');
            
            li.addEventListener('mouseenter', () => actions.style.display = 'flex');
            li.addEventListener('mouseleave', () => actions.style.display = 'none');
            
            clone.querySelector('.stash-apply-btn').addEventListener('click', async (e) => {
                e.stopPropagation();
                try {
                    await window.api.applyStash(repoPath, stash.id);
                    showToast(`Applied ${stash.id}`, 'success');
                    loadStagingData(repoPath);
                } catch(err) { alert('Error applying stash: ' + err.message); }
            });
            
            clone.querySelector('.stash-pop-btn').addEventListener('click', async (e) => {
                e.stopPropagation();
                try {
                    await window.api.popStash(repoPath, stash.id);
                    showToast(`Popped ${stash.id}`, 'success');
                    loadStagingData(repoPath);
                } catch(err) { alert('Error popping stash: ' + err.message); }
            });
            
            clone.querySelector('.stash-drop-btn').addEventListener('click', async (e) => {
                e.stopPropagation();
                if (!confirm(`Are you sure you want to drop ${stash.id}?`)) return;
                try {
                    await window.api.dropStash(repoPath, stash.id);
                    showToast(`Dropped ${stash.id}`, 'success');
                    loadStagingData(repoPath);
                } catch(err) { alert('Error dropping stash: ' + err.message); }
            });

            container.appendChild(clone);
        });
    } catch (err) {
        console.error('Error loading stashes:', err);
    }
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
    
    const tab = tabState.tabs.find(t => t.id === tabState.activeTabId);
    if (tab) {
        tab.activeCommitHash = isStaged ? 'STAGED' : 'UNSTAGED';
        tab.activeFile = file;
        saveTabsState();
    }

    try {
        const diffData = await window.api.getLiveDiff(repoPath, file, isStaged);
        renderMonacoDiff(diffData);
    } catch (err) {
        clearDiffViewer(`<div style="color:red;">Error: ${err.message}</div>`);
    }
}

function closeTab(id) {
    const tabIndex = tabState.tabs.findIndex(t => t.id === id);
    if (tabIndex === -1) return;
    
    const tab = tabState.tabs[tabIndex];
    if (window.api && window.api.unwatchRepo) {
        window.api.unwatchRepo(tab.path);
    }

    tabState.tabs.splice(tabIndex, 1);
    
    if (tabState.tabs.length === 0) {
        tabState.activeTabId = null;
        activeRepoPath = null;
        tabsBar.classList.add('hidden');
        commitsView.classList.add('hidden');
        landingView.classList.remove('hidden');
        document.getElementById('status-bar').classList.add('hidden');
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
        
        li.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            const ctxMenu = document.getElementById('commit-context-menu');
            if (ctxMenu) {
                currentBranchTargetCommit = commit.hash;
                ctxMenu.style.top = `${e.clientY}px`;
                ctxMenu.style.left = `${e.clientX}px`;
                ctxMenu.classList.remove('hidden');
            }
        });

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

    let maxOverallWidth = 60;
    const paddingOffset = 2; // Approximate padding top
    
    const dpr = window.devicePixelRatio || 1;
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

        // Free up any other tracks that were pointing to this commit (merged branches)
        for (let j = 0; j < tracks.length; j++) {
            if (j !== trackIndex && tracks[j] === commit.hash) {
                tracks[j] = null;
            }
        }

        const x = Math.round(15 + (trackIndex * 15)) + 0.5;
        const color = colors[trackIndex % colors.length];
        
        commitCoords[commit.hash] = { x, y: 0, color };

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

        let maxActiveIndex = trackIndex;
        for (let j = 0; j < tracks.length; j++) {
            if (tracks[j]) maxActiveIndex = Math.max(maxActiveIndex, j);
        }
        
        const requiredPadding = 30 + (maxActiveIndex * 15);
        rows[i].style.paddingLeft = requiredPadding + 'px';
        maxOverallWidth = Math.max(maxOverallWidth, requiredPadding + 10);
    });

    const baseContentHeight = rows[0].querySelector('.commit-content').offsetHeight || 24;
    const lastRow = rows[rows.length - 1];
    const totalHeight = lastRow.offsetTop + lastRow.offsetHeight;
    
    canvas.width = Math.floor(maxOverallWidth * dpr);
    canvas.height = Math.floor(totalHeight * dpr);
    canvas.style.width = maxOverallWidth + 'px';
    canvas.style.height = totalHeight + 'px';

    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, maxOverallWidth, totalHeight);
    
    commits.forEach((commit, i) => {
        const coord = commitCoords[commit.hash];
        if (coord) {
            coord.y = Math.round(rows[i].offsetTop + (baseContentHeight / 2) + paddingOffset) + 0.5;
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
                
                if (start.x === end.x) {
                    ctx.lineTo(end.x, end.y);
                } else {
                    const shiftY = Math.min(baseContentHeight, Math.abs(end.y - start.y));
                    const dir = end.y > start.y ? 1 : -1;
                    
                    ctx.bezierCurveTo(
                        start.x, start.y + (shiftY * 0.2 * dir),
                        end.x, start.y + (shiftY * 0.8 * dir),
                        end.x, start.y + (shiftY * dir)
                    );
                    ctx.lineTo(end.x, end.y);
                }
                
                ctx.strokeStyle = idx === 0 ? start.color : end.color;
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';
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
        // Removed the dark stroke to prevent cutout artifacts
    });
}

async function loadCommitDetails(commit, repoPath, commitLi) {
    document.getElementById('details-placeholder').classList.add('hidden');
    document.getElementById('commit-details-content').classList.remove('hidden');

    document.getElementById('detail-message').textContent = commit.message;
    document.getElementById('detail-hash').textContent = commit.hash;
    document.getElementById('detail-author').textContent = commit.author;
    document.getElementById('detail-date').textContent = commit.date;

    clearDiffViewer('<div class="diff-placeholder">Select a file to view its diff</div>');

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
    
    try {
        const diffData = await window.api.getFileDiff(repoPath, hash, file);
        
        renderMonacoDiff(diffData);

        const tab = tabState.tabs.find(t => t.id === tabState.activeTabId);
        if (tab) {
            tab.activeCommitHash = hash;
            tab.activeFile = file;
            saveTabsState();
        }
    } catch (err) {
        clearDiffViewer(`<div style="color:red;">Error: ${err.message}</div>`);
    }
}

function renderMonacoDiff(diffData) {
    clearDiffViewer('');
    
    const container = document.getElementById('diff-viewer');
    if (!window.monaco) {
        container.innerHTML = '<div style="color:red; padding: 1rem;">Monaco Editor is not loaded.</div>';
        return;
    }

    // Determine language from file extension
    const ext = diffData.file.split('.').pop().toLowerCase();
    let language = 'plaintext';
    if (ext === 'js' || ext === 'jsx') language = 'javascript';
    else if (ext === 'ts' || ext === 'tsx') language = 'typescript';
    else if (ext === 'html' || ext === 'htm') language = 'html';
    else if (ext === 'css') language = 'css';
    else if (ext === 'json') language = 'json';
    else if (ext === 'py') language = 'python';
    else if (ext === 'md') language = 'markdown';
    else if (ext === 'sh') language = 'shell';

    const originalModel = window.monaco.editor.createModel(diffData.original || '', language);
    const modifiedModel = window.monaco.editor.createModel(diffData.modified || '', language);

    // Retrieve stored font size or default to 14
    const storedFontSize = parseInt(localStorage.getItem('pulpo-monaco-fontsize')) || 14;

    monacoEditorInstance = window.monaco.editor.createDiffEditor(container, {
        theme: 'vs-dark',
        automaticLayout: true,
        readOnly: true,
        minimap: { enabled: true },
        scrollBeyondLastLine: false,
        renderSideBySide: true, // Standard VS Code side-by-side diff
        fontSize: storedFontSize
    });

    monacoEditorInstance.setModel({
        original: originalModel,
        modified: modifiedModel
    });
}

function clearDiffViewer(placeholderHtml) {
    if (monacoEditorInstance) {
        monacoEditorInstance.dispose();
        monacoEditorInstance = null;
    }
    const diffViewerEl = document.getElementById('diff-viewer');
    if (diffViewerEl) {
        diffViewerEl.innerHTML = placeholderHtml || '';
    }
}

