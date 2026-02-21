import api from './api';

export const authService = {
    login: async (username, password) => {
        // Note: FastAPI OAuth2PasswordRequestForm requires form data
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await api.post('/auth/login', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });
        return response.data;
    },

    register: async (username, password, role) => {
        const response = await api.post('/auth/register', {
            username,
            password,
            role
        });
        return response.data;
    },
};
