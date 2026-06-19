const getFileDiff = require('../../src/core/getFileDiffUseCase');
const child_process = require('child_process');

jest.mock('child_process');

describe('getFileDiffUseCase', () => {
    it('debe devolver el diff de un archivo especifico en un commit', async () => {
        const mockDiff = "diff --git a/file.txt b/file.txt\n-old line\n+new line";
        child_process.exec.mockImplementation((command, options, callback) => {
            if(command.includes('git show')) {
                callback(null, mockDiff, '');
            }
        });

        const diff = await getFileDiff('/fake/path', 'abc1234', 'file.txt');
        expect(diff).toBe(mockDiff);
    });

    it('debe manejar errores al obtener el diff', async () => {
        child_process.exec.mockImplementation((command, options, callback) => {
            callback(new Error('File not found in commit'), '', 'error');
        });

        await expect(getFileDiff('/fake/path', 'abc1234', 'missing.txt')).rejects.toThrow();
    });
});
