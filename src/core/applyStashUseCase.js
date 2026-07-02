const { exec } = require('./gitExec');

function applyStash(repoPath, stashId) {
    return new Promise((resolve, reject) => {
        let command = 'git stash apply';
        if (stashId !== undefined && stashId !== null) {
            command = `git stash apply ${stashId}`;
        }
        exec(command, { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(error);
            }
            resolve(stdout.trim());
        });
    });
}

module.exports = applyStash;
