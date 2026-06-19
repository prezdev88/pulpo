const { exec } = require('child_process');

function checkoutBranch(repoPath, branchName) {
    return new Promise((resolve, reject) => {
        exec(`git checkout ${branchName}`, { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(error);
            }
            resolve(true);
        });
    });
}

module.exports = checkoutBranch;
