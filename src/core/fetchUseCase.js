const gitExec = require('./gitExec');

function fetchUseCase(repoPath) {
    return new Promise((resolve, reject) => {
        gitExec.exec('git fetch', { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(new Error(`Failed to fetch: ${error.message}`));
            }
            resolve(stdout || stderr || 'Fetch successful');
        });
    });
}

module.exports = { fetchUseCase };
