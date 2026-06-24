const util = require('util');
const exec = util.promisify(require('child_process').exec);

async function commitChanges(repoPath, message) {
    try {
        // Escape quotes in the message
        const escapedMessage = message.replace(/"/g, '\\"');
        await exec(`git commit -m "${escapedMessage}"`, { cwd: repoPath });
    } catch (error) {
        throw new Error(`Failed to commit: ${error.message}`);
    }
}

module.exports = { commitChanges };
