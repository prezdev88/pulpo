const gitExec = require('./gitExec');

function pullUseCase(repoPath) {
    return new Promise((resolve, reject) => {
        gitExec.exec('git pull', { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(new Error(`Failed to pull: ${error.message}`));
            }
            resolve(stdout || stderr || 'Pull successful');
        });
    });
}

module.exports = { pullUseCase };
