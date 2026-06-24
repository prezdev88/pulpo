const { exec } = require('./gitExec');

function stashChanges(repoPath) {
    return new Promise((resolve, reject) => {
        exec('git stash', { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(error);
            }
            resolve(stdout.trim());
        });
    });
}

module.exports = stashChanges;
