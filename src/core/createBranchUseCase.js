const { exec } = require('./gitExec');

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
