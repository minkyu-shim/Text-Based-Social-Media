const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

// Singleton refresh promise — prevents multiple concurrent refresh calls
let refreshPromise = null;

function redirectToLogin() {
  localStorage.removeItem('sn_access_token');
  localStorage.removeItem('sn_refresh_token');
  localStorage.removeItem('sn_user_id');
  window.location.href = '/login';
}

async function tryRefreshToken() {
  if (refreshPromise) return refreshPromise;

  const refreshToken = localStorage.getItem('sn_refresh_token');
  if (!refreshToken) {
    redirectToLogin();
    return false;
  }

  refreshPromise = fetch(`${BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  })
    .then(async (res) => {
      if (!res.ok) {
        redirectToLogin();
        return false;
      }
      const data = await res.json();
      localStorage.setItem('sn_access_token', data.access_token);
      return true;
    })
    .catch(() => {
      redirectToLogin();
      return false;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
}

async function request(method, path, body, isRetry = false) {
  const token = localStorage.getItem('sn_access_token');

  const headers = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const options = {
    method,
    headers,
  };
  if (body !== undefined) {
    options.body = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(`${BASE}${path}`, options);
  } catch (err) {
    throw new Error('Network error — could not reach the server.');
  }

  if (res.status === 401 && !isRetry) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      return request(method, path, body, true);
    }
    return null;
  }

  // Parse JSON, but return a shaped object with ok, status, and data
  let data;
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    data = await res.json();
  } else {
    data = null;
  }

  if (!res.ok) {
    const message =
      (data && (data.error || data.message)) ||
      `Request failed with status ${res.status}`;
    const err = new Error(message);
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}

export const api = {
  get: (path) => request('GET', path),
  post: (path, body) => request('POST', path, body),
  patch: (path, body) => request('PATCH', path, body),
  delete: (path, body) => request('DELETE', path, body),
  put: (path, body) => request('PUT', path, body),
};
