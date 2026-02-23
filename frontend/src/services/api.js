import axios from 'axios';

// ─────────────────────────────────────────────────────────────────────────────
// API Client — points to the Flask backend
// VITE_API_URL is set in .env (defaults to http://localhost:5000 for local dev)
// ─────────────────────────────────────────────────────────────────────────────
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const api = axios.create({
    baseURL: BASE_URL,
    timeout: 60000, // 60s — large CSV datasets can take a while
});

/**
 * Upload a CSV file for analysis.
 * Sends a multipart/form-data POST to /analyze.
 * Returns the full analysis response including suspicious_accounts,
 * fraud_rings, summary, and graph_data.
 *
 * @param {File} file - The CSV file object from the browser input
 * @returns {Promise<AxiosResponse>}
 */
export const analyzeCSV = (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
};

/**
 * Health check — verify backend is reachable before upload.
 */
export const checkHealth = () => api.get('/health');