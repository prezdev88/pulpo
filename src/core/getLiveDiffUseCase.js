const util = require('util');
const exec = util.promisify(require('child_process').exec);

async function getLiveDiff(repoPath, file, isStaged) {
    try {
        const cachedFlag = isStaged ? '--cached' : '';
        // If file is newly untracked, git diff won't show anything unless we use a specific approach,
        // but for now standard git diff handles modified files.
        const { stdout } = await exec(`git diff ${cachedFlag} -- "${file}"`, { cwd: repoPath });
        
        if (!stdout && !isStaged) {
            // Check if untracked
            const { stdout: statusOut } = await exec(`git status --porcelain -- "${file}"`, { cwd: repoPath });
            if (statusOut.trim().startsWith('??')) {
                // Untracked file: return its contents as additions
                const fs = require('fs');
                const path = require('path');
                const fullPath = path.join(repoPath, file);
                if (fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory()) {
                    return `Untracked directory: ${file}\n`;
                }
                const content = fs.readFileSync(fullPath, 'utf8');
                const lines = content.split('\n');
                return lines.map(l => `+${l}`).join('\n');
            }
        }
        
        return stdout;
    } catch (error) {
        throw new Error(`Failed to get diff: ${error.message}`);
    }
}

module.exports = { getLiveDiff };
