const { exec } = require('./gitExec');

function listStashes(repoPath) {
    return new Promise((resolve, reject) => {
        // Format: stash@{0}|WIP on main: 1234567|2 days ago
        const format = "%gd|%gs|%cr";
        exec(`git stash list --format="${format}"`, { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(error);
            }
            const stashes = stdout.trim().split('\n').filter(line => line.length > 0).map(line => {
                const parts = line.split('|');
                return {
                    id: parts[0],
                    message: parts[1],
                    date: parts[2]
                };
            });
            resolve(stashes);
        });
    });
}

module.exports = listStashes;
