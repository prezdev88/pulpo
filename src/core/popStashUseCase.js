const { exec } = require('./gitExec');

function popStash(repoPath) {
    return new Promise((resolve, reject) => {
        exec('git stash pop', { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(error);
            }
            resolve(stdout.trim());
        });
    });
}

module.exports = popStash;
