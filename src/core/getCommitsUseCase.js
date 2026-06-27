const { exec } = require('./gitExec');

function getCommits(repoPath) {
    return new Promise((resolve, reject) => {
        const command = `git log --pretty=format:"%h||%p||%s||%an <%ae>||%ad" --date=format:"%d-%b-%Y %H:%M"`;
        
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
