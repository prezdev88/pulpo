const { exec } = require('./gitExec');

function dropStash(repoPath, stashId) {
    return new Promise((resolve, reject) => {
        let command = 'git stash drop';
        if (stashId !== undefined && stashId !== null) {
            command = `git stash drop ${stashId}`;
        }
        exec(command, { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(error);
            }
            resolve(stdout.trim());
        });
    });
}

module.exports = dropStash;
