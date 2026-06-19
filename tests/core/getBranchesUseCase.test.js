const getBranches = require('../../src/core/getBranchesUseCase');
const child_process = require('child_process');

jest.mock('child_process');

describe('getBranchesUseCase', () => {
    it('debe devolver la lista de ramas y marcar la activa', async () => {
        const mockGitOutput = `  feature-a\n* master\n  test-branch`;
        
        child_process.exec.mockImplementation((command, options, callback) => {
            if(command.includes('git branch')) {
                callback(null, mockGitOutput, '');
            }
        });

        const result = await getBranches('/fake/path');
        expect(result.branches).toHaveLength(3);
        expect(result.activeBranch).toBe('master');
        expect(result.branches).toContain('feature-a');
        expect(result.branches).toContain('master');
        expect(result.branches).toContain('test-branch');
    });

    it('debe rechazar la promesa si hay un error', async () => {
        child_process.exec.mockImplementation((command, options, callback) => {
            callback(new Error('Git error'), '', 'stderr');
        });

        await expect(getBranches('/fake/path')).rejects.toThrow('Git error');
    });
});
