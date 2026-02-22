import api from './api';

export const auditService = {
    getLogs: async (filters = {}) => {
        const params = new URLSearchParams();
        if (filters.mode) params.append('mode', filters.mode);
        if (filters.decision) params.append('decision', filters.decision);
        if (filters.documentId) params.append('document_id', filters.documentId);
        if (filters.userId) params.append('user_id', filters.userId);
        if (filters.query_hash) params.append('query_hash', filters.query_hash);

        const url = `/audit/logs?${params.toString()}`;
        const response = await api.get(url);
        return response.data;
    },

    getReliability: async () => {
        const response = await api.get('/audit/reliability');
        return response.data;
    }
};
