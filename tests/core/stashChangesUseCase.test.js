const stashChanges = require('../../src/core/stashChangesUseCase');
const child_process = require('child_process');

jest.mock('child_process');

describe('stashChangesUseCase', () => {
    it('debe ejecutar git stash y devolver el mensaje de exito', async () => {
        child_process.exec.mockImplementation((command, options, callback) => {
            if(command.includes('git stash')) {
                callback(null, 'Saved working directory and index state WIP', '');
            }
        });

        const result = await stashChanges('/fake/path');
        expect(result).toBe('Saved working directory and index state WIP');
    });

    it('debe rechazar si git stash falla', async () => {
        child_process.exec.mockImplementation((command, options, callback) => {
            callback(new Error('Git stash failed'), '', 'error');
        });

        await expect(stashChanges('/fake/path')).rejects.toThrow();
    });
});
