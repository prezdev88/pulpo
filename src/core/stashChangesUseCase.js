const { exec } = require('./gitExec');

function stashChanges(repoPath, message) {
    return new Promise((resolve, reject) => {
        const cmd = message ? `git stash push -m "${message.replace(/"/g, '\\"')}"` : 'git stash';
        exec(cmd, { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(error);
            }
            resolve(stdout.trim());
        });
    });
}

module.exports = stashChanges;
