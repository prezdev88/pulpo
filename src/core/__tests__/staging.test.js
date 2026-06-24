const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');
const { getStatus } = require('../getStatusUseCase');
const { stageFiles } = require('../stageFilesUseCase');
const { unstageFiles } = require('../unstageFilesUseCase');
const { commitChanges } = require('../commitChangesUseCase');
const { getLiveDiff } = require('../getLiveDiffUseCase');

describe('Staging & Commit Use Cases', () => {
    let testRepoPath;

    beforeEach(() => {
        testRepoPath = fs.mkdtempSync(path.join(os.tmpdir(), 'pulpo-staging-test-'));
        execSync('git init', { cwd: testRepoPath });
        execSync('git config user.name "Test User"', { cwd: testRepoPath });
        execSync('git config user.email "test@example.com"', { cwd: testRepoPath });

        // Create initial commit
        fs.writeFileSync(path.join(testRepoPath, 'initial.txt'), 'Hello Pulpo');
        execSync('git add .', { cwd: testRepoPath });
        execSync('git commit -m "Initial commit"', { cwd: testRepoPath });
    });

    afterEach(() => {
        fs.rmSync(testRepoPath, { recursive: true, force: true });
    });

    test('getStatus returns empty when clean', async () => {
        const status = await getStatus(testRepoPath);
        expect(status.staged).toEqual([]);
        expect(status.unstaged).toEqual([]);
    });

    test('getStatus identifies unstaged and staged files', async () => {
        // Modify existing
        fs.writeFileSync(path.join(testRepoPath, 'initial.txt'), 'Hello Pulpo Modified');
        // Create new
        fs.writeFileSync(path.join(testRepoPath, 'new.txt'), 'New File');

        let status = await getStatus(testRepoPath);
        expect(status.staged.length).toBe(0);
        expect(status.unstaged.length).toBe(2);
        
        const files = status.unstaged.map(f => f.file).sort();
        expect(files).toEqual(['initial.txt', 'new.txt']);

        // Stage one file
        await stageFiles(testRepoPath, ['new.txt']);
        status = await getStatus(testRepoPath);
        expect(status.staged.length).toBe(1);
        expect(status.staged[0].file).toBe('new.txt');
        expect(status.unstaged.length).toBe(1);
        expect(status.unstaged[0].file).toBe('initial.txt');
    });

    test('unstageFiles removes file from staging', async () => {
        fs.writeFileSync(path.join(testRepoPath, 'new.txt'), 'New File');
        await stageFiles(testRepoPath, ['.']);
        
        let status = await getStatus(testRepoPath);
        expect(status.staged.length).toBe(1);

        await unstageFiles(testRepoPath, ['new.txt']);
        status = await getStatus(testRepoPath);
        expect(status.staged.length).toBe(0);
        expect(status.unstaged.length).toBe(1);
    });

    test('commitChanges creates a new commit', async () => {
        fs.writeFileSync(path.join(testRepoPath, 'new.txt'), 'New File');
        await stageFiles(testRepoPath, ['.']);
        
        await commitChanges(testRepoPath, 'My new feature');
        
        const log = execSync('git log -1 --pretty=%B', { cwd: testRepoPath }).toString().trim();
        expect(log).toBe('My new feature');
        
        const status = await getStatus(testRepoPath);
        expect(status.staged.length).toBe(0);
        expect(status.unstaged.length).toBe(0);
    });

    test('getLiveDiff returns diff for unstaged and staged files', async () => {
        fs.writeFileSync(path.join(testRepoPath, 'initial.txt'), 'Hello Pulpo Modified');
        
        // Unstaged diff
        const unstagedDiff = await getLiveDiff(testRepoPath, 'initial.txt', false);
        expect(unstagedDiff).toContain('-Hello Pulpo');
        expect(unstagedDiff).toContain('+Hello Pulpo Modified');

        // Stage it
        await stageFiles(testRepoPath, ['.']);
        
        // Staged diff
        const stagedDiff = await getLiveDiff(testRepoPath, 'initial.txt', true);
        expect(stagedDiff).toContain('-Hello Pulpo');
        expect(stagedDiff).toContain('+Hello Pulpo Modified');
        
        // Unstaged diff should now be empty
        const unstagedDiffEmpty = await getLiveDiff(testRepoPath, 'initial.txt', false);
        expect(unstagedDiffEmpty).toBe('');
    });
});
