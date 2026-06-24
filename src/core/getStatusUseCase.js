const util = require('util');
const exec = util.promisify(require('child_process').exec);

async function getStatus(repoPath) {
    try {
        const { stdout } = await exec('git status --porcelain', { cwd: repoPath });
        const lines = stdout.split('\n').filter(line => line.trim() !== '');
        
        const staged = [];
        const unstaged = [];
        
        lines.forEach(line => {
            // Status is the first two characters.
            // X is the index status (staged), Y is the working tree status (unstaged)
            const x = line[0];
            const y = line[1];
            const file = line.substring(3).trim(); // Remove status and space
            
            // X matches: M (modified), A (added), D (deleted), R (renamed), C (copied)
            if (x !== ' ' && x !== '?') {
                staged.push({ status: x, file });
            }
            
            // Y matches: M (modified), D (deleted), ? (untracked)
            if (y !== ' ') {
                unstaged.push({ status: y, file });
            }
        });
        
        return { staged, unstaged };
    } catch (error) {
        throw new Error(`Failed to get git status: ${error.message}`);
    }
}

module.exports = { getStatus };
