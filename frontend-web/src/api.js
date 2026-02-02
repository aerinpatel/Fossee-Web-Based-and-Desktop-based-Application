import axios from 'axios';

/**
 * Axios instance configured with the base API URL.
 * Handles automatic attachment of the Authorization header from localStorage.
 */
const api = axios.create({
    baseURL: 'http://localhost:8000/api/',
});

// Initialize token from localStorage if it exists
const storedToken = localStorage.getItem('flowdrishti_token');
if (storedToken) {
    api.defaults.headers.common['Authorization'] = `Token ${storedToken}`;
}

/**
 * Updates the Authorization header for all future requests and persists the token.
 * @param {string|null} token - The REST API token or null to clear authentication.
 */
export const setAuthToken = (token) => {
    if (token) {
        localStorage.setItem('flowdrishti_token', token);
        api.defaults.headers.common['Authorization'] = `Token ${token}`;
    } else {
        localStorage.removeItem('flowdrishti_token');
        delete api.defaults.headers.common['Authorization'];
    }
};

export default api;
