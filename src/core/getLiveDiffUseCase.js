const util = require('util');
const exec = util.promisify(require('child_process').exec);
const fs = require('fs');
const path = require('path');

async function getLiveDiff(repoPath, file, isStaged) {
    try {
        let original = '';
        let modified = '';

        if (isStaged) {
            // Staged diff: original is HEAD, modified is Index (Staging Area)
            try {
                const { stdout } = await exec(`git show HEAD:"${file}"`, { cwd: repoPath, maxBuffer: 1024 * 1024 * 10 });
                original = stdout;
            } catch (e) { original = ''; }

            try {
                const { stdout } = await exec(`git show :"${file}"`, { cwd: repoPath, maxBuffer: 1024 * 1024 * 10 });
                modified = stdout;
            } catch (e) { modified = ''; }
        } else {
            // Unstaged diff: original is Index (or HEAD if empty index), modified is Working Directory
            try {
                const { stdout } = await exec(`git show :"${file}"`, { cwd: repoPath, maxBuffer: 1024 * 1024 * 10 });
                original = stdout;
            } catch (e) { 
                // If not in index, try HEAD
                try {
                    const { stdout } = await exec(`git show HEAD:"${file}"`, { cwd: repoPath, maxBuffer: 1024 * 1024 * 10 });
                    original = stdout;
                } catch (e2) {
                    original = '';
                }
            }

            const fullPath = path.join(repoPath, file);
            if (fs.existsSync(fullPath)) {
                if (fs.statSync(fullPath).isDirectory()) {
                    modified = 'Directory';
                } else {
                    modified = fs.readFileSync(fullPath, 'utf8');
                }
            } else {
                modified = ''; // File deleted
            }
        }

        return { original, modified, file };
    } catch (error) {
        throw new Error(`Failed to get diff: ${error.message}`);
    }
}

module.exports = { getLiveDiff };
