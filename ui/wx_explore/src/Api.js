import axios from 'axios';

const api = axios.create({
    baseURL: process.env.REACT_APP_API_ENDPOINT,
    timeout: 30000,
});

export const getSources = async () => {
    try {
        const response = await api.get('/sources');
        return response.data;
    } catch (error) {
        // Enhance error message based on the type of error
        const message = error.response?.status === 404 
            ? 'Weather sources endpoint not found'
            : error.response?.status >= 500
            ? 'Server error while fetching weather sources'
            : 'Failed to fetch weather sources';
        
        throw new Error(message);
    }
};

export default api;