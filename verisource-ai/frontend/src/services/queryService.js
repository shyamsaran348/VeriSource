import api from './api';

export const queryService = {
    submitQuery: async (documentId, mode, query) => {
        const response = await api.post('/query', {
            document_id: documentId,
            mode: mode,
            query: query
        });
        return response.data;
    },
};
