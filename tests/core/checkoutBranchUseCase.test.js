const checkoutBranch = require('../../src/core/checkoutBranchUseCase');
const child_process = require('child_process');

jest.mock('child_process');

describe('checkoutBranchUseCase', () => {
    it('debe ejecutar git checkout con la rama especificada', async () => {
        child_process.exec.mockImplementation((command, options, callback) => {
            if(command.includes('git checkout feature-branch')) {
                callback(null, 'Switched to branch feature-branch', '');
            }
        });

        const result = await checkoutBranch('/fake/path', 'feature-branch');
        expect(result).toBe(true);
    });

    it('debe rechazar si la rama no existe o hay error', async () => {
        child_process.exec.mockImplementation((command, options, callback) => {
            callback(new Error('Pathspec did not match any file(s)'), '', 'error');
        });

        await expect(checkoutBranch('/fake/path', 'invalid-branch')).rejects.toThrow();
    });
});
