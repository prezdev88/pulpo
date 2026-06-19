const createBranch = require('../../src/core/createBranchUseCase');
const child_process = require('child_process');

jest.mock('child_process');

describe('createBranchUseCase', () => {
    it('debe ejecutar git checkout -b con el nombre de la nueva rama', async () => {
        child_process.exec.mockImplementation((command, options, callback) => {
            if(command.includes('git checkout -b new-feature')) {
                callback(null, 'Switched to a new branch new-feature', '');
            }
        });

        const result = await createBranch('/fake/path', 'new-feature');
        expect(result).toBe(true);
    });

    it('debe rechazar si hay un error al crear la rama', async () => {
        child_process.exec.mockImplementation((command, options, callback) => {
            callback(new Error('A branch named new-feature already exists'), '', 'error');
        });

        await expect(createBranch('/fake/path', 'new-feature')).rejects.toThrow();
    });
});
