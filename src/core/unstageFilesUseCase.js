const util = require('util');
const exec = util.promisify(require('child_process').exec);

async function unstageFiles(repoPath, files) {
    try {
        const filesArg = files.map(f => `"${f}"`).join(' ');
        await exec(`git reset HEAD ${filesArg}`, { cwd: repoPath });
    } catch (error) {
        throw new Error(`Failed to unstage files: ${error.message}`);
    }
}

module.exports = { unstageFiles };
