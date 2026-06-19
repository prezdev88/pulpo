const { exec } = require('child_process');

function getCommits(repoPath) {
    return new Promise((resolve, reject) => {
        // git log format: %h||%p||%s||%an||%ad
        const command = `git log --pretty=format:"%h||%p||%s||%an||%ad" --date=format:"%Y-%m-%d %H:%M"`;
        
        exec(command, { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(error);
            }
            
            if (!stdout || !stdout.trim()) {
                return resolve([]);
            }

            const commits = stdout.trim().split('\n').map(line => {
                const [hash, parentHashes, message, author, date] = line.split('||');
                const parents = parentHashes ? parentHashes.split(' ') : [];
                return { hash, parents, message, author, date };
            });

            resolve(commits);
        });
    });
}

module.exports = { getCommits };
