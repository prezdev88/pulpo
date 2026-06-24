const { exec } = require('child_process');

function getFileDiff(repoPath, hash, file) {
    return new Promise((resolve, reject) => {
        exec(`git show --format="" ${hash} -- "${file}"`, { cwd: repoPath }, (error, stdout, stderr) => {
            if (error) {
                return reject(error);
            }
            resolve(stdout.trimStart());
        });
    });
}

module.exports = getFileDiff;
