const gitExec = require('./gitExec');

function getRemoteUrl(repoPath) {
    return new Promise((resolve) => {
        gitExec.exec('git remote get-url origin', { cwd: repoPath }, (error, stdout) => {
            if (error || !stdout) {
                resolve('');
            } else {
                resolve(stdout.trim());
            }
        });
    });
}

module.exports = { getRemoteUrl };
