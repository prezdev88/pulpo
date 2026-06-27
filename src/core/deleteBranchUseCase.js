const { exec } = require('./gitExec');

function deleteBranch(repoPath, branchName) {
    return new Promise((resolve, reject) => {
        exec(`git branch -D ${branchName}`, { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(error);
            }
            resolve(true);
        });
    });
}

module.exports = deleteBranch;
