const { exec } = require('./gitExec');

function createBranch(repoPath, branchName, commitHash) {
    return new Promise((resolve, reject) => {
        const target = commitHash ? ` ${commitHash}` : '';
        exec(`git checkout -b ${branchName}${target}`, { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(error);
            }
            resolve(true);
        });
    });
}

module.exports = createBranch;
