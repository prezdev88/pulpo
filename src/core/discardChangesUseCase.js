const { exec } = require('./gitExec');

function discardChanges(repoPath, files) {
    return new Promise(async (resolve, reject) => {
        if (!files || files.length === 0) return resolve();
        
        if (files.length === 1 && files[0] === '.') {
            const command = `git reset HEAD . >/dev/null 2>&1; git clean -fd; git checkout -- . 2>/dev/null || true`;
            exec(command, { cwd: repoPath }, (error, stdout, stderr) => {
                if (error) return reject(error);
                resolve(true);
            });
            return;
        }

        const chunkSize = 50;
        for (let i = 0; i < files.length; i += chunkSize) {
            const chunk = files.slice(i, i + chunkSize);
            // Quote files to prevent issues with spaces in filenames
            const target = chunk.map(f => `"${f.replace(/"/g, '\\"')}"`).join(' ');
            const command = `git reset HEAD ${target} >/dev/null 2>&1; git clean -fd ${target}; git checkout -- ${target} 2>/dev/null || true`;
            
            try {
                await new Promise((res, rej) => {
                    exec(command, { cwd: repoPath }, (err) => {
                        if (err) return rej(err);
                        res();
                    });
                });
            } catch (err) {
                return reject(err);
            }
        }
        resolve(true);
    });
}

module.exports = { discardChanges };
