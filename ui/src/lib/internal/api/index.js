import axios from 'axios';

class Api {
    _baseUrl = 'http://localhost:8000';

    constructor() {

    }


    async get(path) {
        try {
            const response = await axios.get(`${this._baseUrl}${path}`);
            return response.data;
        } catch (error) {
            return error.response.data;
        }
    }

    async post(path, data) {
        try {
            const response = await axios.post(`${this._baseUrl}${path}`, data);
            return response.data;
        } catch (error) {
            return error.response.data;
        }
    }

    async listDirectories() {
        return await this.get('/list_directories');
    }

    async getImageByPath(path) {
        return await this.post(`/get_image_by_path`, [path]);
    }

    async getRunIds() {
        return await this.get('/get_run_ids');
    }

    async getEvaluationResults(runId) {
        return await this.get(`/get_results_by_run_id?run_id=${runId}`);
    }

    async getEvaluationIds(runId) {
        return await this.get(`/get_evaluation_ids?run_id=${runId}`);
    }

    async getModules() {
        return await this.get('/get_modules');
    }

    async getMethods(module) {
        return await this.get(`/get_methods/${module}`);
    }

    async validatePipe(pipe) {
        return await this.post(`/validate_config`, pipe);
    }

    async validatePipeline(pipeline) {
        return await this.post(`/validate_pipeline_config`, pipeline);
    }

    async runPipeline(pipeline, runId) {

        const response = await fetch(`${this._baseUrl}/run_pipeline?run_id=${runId}`, {
            method: 'POST',
            body: JSON.stringify(pipeline),
            headers: {
                "Content-Type": "application/json",
            }
        });

        const reader = response?.body?.getReader();

        return reader;
    }
}

const API = new Api();

export default API;