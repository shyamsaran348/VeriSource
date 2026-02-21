import api from './api';

export const documentService = {
    getDocuments: async (mode = null) => {
        // Fix for Safari 307 strict CORS redirects dropping headers
        const url = mode ? `/documents/?mode=${mode}` : '/documents/';
        const response = await api.get(url);
        return response.data;
    },

    uploadDocument: async (file, name, mode, version, authority) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('name', name);
        formData.append('mode', mode);
        formData.append('version', version);
        formData.append('authority', authority);

        const response = await api.post('/ingestion/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            // Increase timeout for uploads/processing
            timeout: 60000
        });
        return response.data;
    },

    deleteDocument: async (documentId) => {
        // Fix for Safari 307 strict CORS redirects dropping headers
        const response = await api.delete(`/documents/${documentId}/`);
        return response.data;
    }
};
