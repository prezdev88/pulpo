const { exec } = require('./gitExec');

function popStash(repoPath, stashId) {
    return new Promise((resolve, reject) => {
        const cmd = stashId ? `git stash pop "${stashId}"` : 'git stash pop';
        exec(cmd, { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(error);
            }
            resolve(stdout.trim());
        });
    });
}

module.exports = popStash;
