const { exec } = require('child_process');

function getCommitFiles(repoPath, hash) {
    return new Promise((resolve, reject) => {
        exec(`git diff-tree --root --no-commit-id --name-status -r ${hash}`, { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(error);
            }
            const files = stdout.split('\n').filter(f => f.trim().length > 0).map(f => {
                const parts = f.split('\t');
                const status = parts[0].charAt(0);
                const file = parts[1];
                return { status, file };
            });
            resolve(files);
        });
    });
}

module.exports = getCommitFiles;
