const popStash = require('../../src/core/popStashUseCase');
const child_process = require('child_process');

jest.mock('child_process');

describe('popStashUseCase', () => {
    it('debe ejecutar git stash pop y devolver exito', async () => {
        child_process.exec.mockImplementation((command, options, callback) => {
            if(command.includes('git stash pop')) {
                callback(null, 'Dropped refs/stash@{0}', '');
            }
        });

        const result = await popStash('/fake/path');
        expect(result).toBe('Dropped refs/stash@{0}');
    });

    it('debe rechazar si git stash pop falla por conflictos u otros motivos', async () => {
        child_process.exec.mockImplementation((command, options, callback) => {
            callback(new Error('Merge conflict in file.txt'), '', 'error');
        });

        await expect(popStash('/fake/path')).rejects.toThrow();
    });
});
