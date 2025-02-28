import axios from 'axios';

const api = axios.create({
    baseURL: process.env.REACT_APP_API_ENDPOINT,
    timeout: 30000,
});

export const getSources = () => {
    return api.get('/api/sources');
};

export default api;