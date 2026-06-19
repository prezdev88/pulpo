const getCommitFiles = require('../../src/core/getCommitFilesUseCase');
const child_process = require('child_process');

jest.mock('child_process');

describe('getCommitFilesUseCase', () => {
    it('debe devolver la lista de archivos modificados en un commit', async () => {
        const mockOutput = "src/main.js\nsrc/renderer/app.js\n";
        child_process.exec.mockImplementation((command, options, callback) => {
            if(command.includes('git diff-tree')) {
                callback(null, mockOutput, '');
            }
        });

        const files = await getCommitFiles('/fake/path', 'abc1234');
        expect(files).toHaveLength(2);
        expect(files[0]).toBe('src/main.js');
        expect(files[1]).toBe('src/renderer/app.js');
    });

    it('debe rechazar si el comando falla', async () => {
        child_process.exec.mockImplementation((command, options, callback) => {
            callback(new Error('Git error'), '', 'error');
        });

        await expect(getCommitFiles('/fake/path', 'invalid_hash')).rejects.toThrow();
    });
});
