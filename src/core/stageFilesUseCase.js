const util = require('util');
const exec = util.promisify(require('child_process').exec);

async function stageFiles(repoPath, files) {
    try {
        const filesArg = files.map(f => `"${f}"`).join(' ');
        await exec(`git add ${filesArg}`, { cwd: repoPath });
    } catch (error) {
        throw new Error(`Failed to stage files: ${error.message}`);
    }
}

module.exports = { stageFiles };
