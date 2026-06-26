const util = require('util');
const exec = util.promisify(require('child_process').exec);

async function getStatus(repoPath) {
    try {
        const { stdout } = await exec('git status --porcelain -b', { cwd: repoPath });
        const lines = stdout.split('\n').filter(line => line.trim() !== '');
        
        const staged = [];
        const unstaged = [];
        let ahead = 0;
        
        lines.forEach(line => {
            if (line.startsWith('##')) {
                if (line.includes('ahead ')) {
                    const match = line.match(/ahead (\d+)/);
                    if (match) ahead = parseInt(match[1]);
                } else if (!line.includes('...') && !line.includes('no branch')) {
                    ahead = 1; // Publish new branch
                }
                return;
            }
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
        
        return { staged, unstaged, ahead };
    } catch (error) {
        throw new Error(`Failed to get git status: ${error.message}`);
    }
}

module.exports = { getStatus };
