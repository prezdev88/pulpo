const { selectRepository } = require('../../src/core/selectRepositoryUseCase');
const electron = require('electron');

jest.mock('electron', () => ({
    dialog: {
        showOpenDialog: jest.fn()
    }
}));

describe('selectRepositoryUseCase', () => {
    it('debe devolver la ruta seleccionada', async () => {
        electron.dialog.showOpenDialog.mockResolvedValue({
            canceled: false,
            filePaths: ['/ruta/al/repositorio']
        });

        const repoPath = await selectRepository();
        expect(repoPath).toBe('/ruta/al/repositorio');
    });

    it('debe devolver null si el usuario cancela', async () => {
        electron.dialog.showOpenDialog.mockResolvedValue({
            canceled: true,
            filePaths: []
        });

        const repoPath = await selectRepository();
        expect(repoPath).toBeNull();
    });
});
