const { exec } = require('./gitExec');

function getBranches(repoPath) {
    return new Promise((resolve, reject) => {
        exec('git branch', { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(error);
            }
            const lines = stdout.split('\n').filter(line => line.trim().length > 0);
            const branches = [];
            let activeBranch = null;

            lines.forEach(line => {
                const isCurrent = line.startsWith('*');
                const branchName = line.replace('*', '').trim();
                branches.push(branchName);
                if (isCurrent) {
                    activeBranch = branchName;
                }
            });

            resolve({ branches, activeBranch });
        });
    });
}

module.exports = getBranches;
