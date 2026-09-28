const API_URL = '/api/requests';

async function apiRequest(url, options = {}) {
    let response;
    try {
        response = await fetch(url, options);
    } catch (error) {
        throw new Error('Не удалось связаться с сервером');
    }

    const result = response.status === 204 ? null : await response.json().catch(() => null);
    if (!response.ok) {
        const error = new Error(result?.error?.message || 'Ошибка запроса к серверу');
        error.errors = result?.error?.details || {};
        error.status = response.status;
        throw error;
    }
    return result;
}

function getStudents(filters = {}) {
    const entries = Object.entries(filters);
    if (entries.length > 3) {
        return apiRequest(API_URL, {
            method: 'QUERY',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(filters)
        });
    }
    const query = new URLSearchParams(filters).toString();
    return apiRequest(query ? `${API_URL}?${query}` : API_URL);
}

function getStudentByIsu(isu) {
    return apiRequest(`${API_URL}/${encodeURIComponent(isu)}`);
}

function addStudent(student) {
    return apiRequest(API_URL, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(student)
    });
}

function updateStudent(oldIsu, student) {
    return apiRequest(`${API_URL}/${encodeURIComponent(oldIsu)}`, {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(student)
    });
}

function deleteStudent(isu) {
    return apiRequest(`${API_URL}/${encodeURIComponent(isu)}`, {method: 'DELETE'});
}
