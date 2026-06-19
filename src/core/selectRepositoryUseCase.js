const { dialog } = require('electron');

async function selectRepository() {
    const result = await dialog.showOpenDialog({
        properties: ['openDirectory']
    });

    if (result.canceled) {
        return null;
    } else {
        return result.filePaths[0];
    }
}

module.exports = { selectRepository };
