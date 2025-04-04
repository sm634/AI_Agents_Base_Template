import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // Update if hosted elsewhere
});

export const askQuery = async (query: string) => {
  const response = await api.post('/ask', { query });
  return response.data;
};
