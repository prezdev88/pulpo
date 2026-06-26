const gitExec = require('./gitExec');

function pushUseCase(repoPath) {
    return new Promise((resolve, reject) => {
        gitExec.exec('git push', { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(new Error(`Failed to push: ${error.message}`));
            }
            resolve(stdout || stderr || 'Push successful');
        });
    });
}

module.exports = { pushUseCase };
