import React, { createContext, useState, useEffect, useContext } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if token exists in localStorage
        const token = localStorage.getItem('access_token');
        const role = localStorage.getItem('user_role');
        const username = localStorage.getItem('user_name');

        if (token && role) {
            setUser({ token, role, username });
        }

        setLoading(false);
    }, []);

    const login = (userData) => {
        localStorage.setItem('access_token', userData.access_token);

        // Use exact role and username from the backend response
        const role = userData.role || 'student';
        const username = userData.username || 'User';

        localStorage.setItem('user_role', role);
        localStorage.setItem('user_name', username);

        setUser({
            token: userData.access_token,
            role: role,
            username: username
        });
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_role');
        localStorage.removeItem('user_name');
        setUser(null);
    };

    const hasRole = (role) => {
        return user?.role === role;
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, hasRole }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
