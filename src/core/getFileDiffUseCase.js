const util = require('util');
const exec = util.promisify(require('child_process').exec);

async function getFileDiff(repoPath, hash, file) {
    try {
        let modified = '';
        try {
            const { stdout } = await exec(`git show ${hash}:"${file}"`, { cwd: repoPath, maxBuffer: 1024 * 1024 * 10 });
            modified = stdout;
        } catch (e) { modified = ''; }

        let original = '';
        try {
            const { stdout } = await exec(`git show ${hash}^:"${file}"`, { cwd: repoPath, maxBuffer: 1024 * 1024 * 10 });
            original = stdout;
        } catch (e) { original = ''; }

        return { original, modified, file };
    } catch (error) {
        throw new Error(`Failed to get file contents: ${error.message}`);
    }
}

module.exports = getFileDiff;
