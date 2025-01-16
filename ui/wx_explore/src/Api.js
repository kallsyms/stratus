import axios from 'axios';

const api = axios.create({
    baseURL: process.env.REACT_APP_API_ENDPOINT,
    timeout: 30000,
});

// Add response interceptor
api.interceptors.response.use(
    (response) => {
        // Any status code within the range of 2xx triggers this function
        return response;
    },
    (error) => {
        // Transform error into a standardized format
        let errorMessage = 'An unexpected error occurred';
        
        if (error.response) {
            // Server responded with a status code outside of 2xx
            errorMessage = error.response.data?.message || `Error: ${error.response.status} ${error.response.statusText}`;
        } else if (error.request) {
            // Request was made but no response received
            errorMessage = 'No response received from server';
            if (error.code === 'ECONNABORTED') {
                errorMessage = 'Request timed out';
            }
        }

        // Create standardized error object
        const standardError = {
            message: errorMessage,
            status: error.response?.status || 500,
            originalError: error
        };

        return Promise.reject(standardError);
    }
);

export default api;