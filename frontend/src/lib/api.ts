const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
}

async function handleResponse<T>(res: Response, url: string, init?: RequestInit): Promise<T> {
  if (res.status === 401) {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      try {
        const refreshRes = await fetch(`${API_BASE || ''}/api/v1/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
        if (refreshRes.ok) {
          const data = await refreshRes.json();
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);
          const retryRes = await fetch(url, { ...init, headers: getAuthHeaders() });
          return handleResponse(retryRes, url, init);
        }
      } catch {
        /* fall through */
      }
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
    throw new Error('Session expired');
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail));
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

const base = API_BASE || '';

export const api = {
  get: <T>(path: string) => {
    const url = `${base}/api/v1${path.startsWith('/') ? path : '/' + path}`;
    return fetch(url, { headers: getAuthHeaders() }).then((r) => handleResponse<T>(r, url));
  },
  post: <T>(path: string, body?: unknown) => {
    const url = `${base}/api/v1${path.startsWith('/') ? path : '/' + path}`;
    const init: RequestInit = {
      method: 'POST',
      headers: getAuthHeaders(),
      body: body ? JSON.stringify(body) : undefined,
    };
    return fetch(url, init).then((r) => handleResponse<T>(r, url, init));
  },
  put: <T>(path: string, body: unknown) => {
    const url = `${base}/api/v1${path.startsWith('/') ? path : '/' + path}`;
    const init: RequestInit = {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(body),
    };
    return fetch(url, init).then((r) => handleResponse<T>(r, url, init));
  },
  delete: <T>(path: string) => {
    const url = `${base}/api/v1${path.startsWith('/') ? path : '/' + path}`;
    return fetch(url, { method: 'DELETE', headers: getAuthHeaders() }).then((r) =>
      handleResponse<T>(r, url)
    );
  },
  upload: async <T>(path: string, file: File, fields: Record<string, string>) => {
    const form = new FormData();
    form.append('file', file);
    Object.entries(fields).forEach(([k, v]) => form.append(k, v));
    const token = localStorage.getItem('access_token');
    const url = `${base}/api/v1${path.startsWith('/') ? path : '/' + path}`;
    const init: RequestInit = {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: form,
    };
    const res = await fetch(url, init);
    return handleResponse<T>(res, url, init);
  },
};
