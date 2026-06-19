const { exec } = require('child_process');

function getCommitFiles(repoPath, hash) {
    return new Promise((resolve, reject) => {
        exec(`git diff-tree --no-commit-id --name-only -r ${hash}`, { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(error);
            }
            const files = stdout.split('\n').map(f => f.trim()).filter(f => f.length > 0);
            resolve(files);
        });
    });
}

module.exports = getCommitFiles;
