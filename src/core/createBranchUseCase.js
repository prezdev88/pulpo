const { exec } = require('child_process');

function createBranch(repoPath, branchName) {
    return new Promise((resolve, reject) => {
        exec(`git checkout -b ${branchName}`, { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(error);
            }
            resolve(true);
        });
    });
}

module.exports = createBranch;
