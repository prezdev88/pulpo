const { getCommits } = require('../../src/core/getCommitsUseCase');
const child_process = require('child_process');

jest.mock('child_process');

describe('getCommitsUseCase', () => {
    it('debe devolver una lista estructurada de commits asincronamente', async () => {
        const mockStdout = 'a1b2c3d||d4e5f6g||Fix bug||John Doe||2023-01-01 12:00\n' +
                           'd4e5f6g||||Initial commit||John Doe||2023-01-01 10:00';
        
        child_process.exec.mockImplementation((command, options, callback) => {
            if(command.includes('git log')) {
                callback(null, mockStdout, '');
            } else {
                callback(new Error('Comando inesperado'), '', '');
            }
        });

        const commits = await getCommits('/fake/path');
        
        expect(commits).toHaveLength(2);
        expect(commits[0]).toEqual({
            hash: 'a1b2c3d',
            parents: ['d4e5f6g'],
            message: 'Fix bug',
            author: 'John Doe',
            date: '2023-01-01 12:00'
        });
        expect(commits[1]).toEqual({
            hash: 'd4e5f6g',
            parents: [],
            message: 'Initial commit',
            author: 'John Doe',
            date: '2023-01-01 10:00'
        });
        expect(child_process.exec).toHaveBeenCalled();
    });

    it('debe manejar errores si el directorio no es un repositorio git', async () => {
        child_process.exec.mockImplementation((command, options, callback) => {
            callback(new Error('fatal: not a git repository'), '', 'fatal: not a git repository');
        });

        await expect(getCommits('/invalid/path')).rejects.toThrow('fatal: not a git repository');
    });
});
