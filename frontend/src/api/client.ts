// Connect directly to backend during dev to avoid sandbox node proxy restrictions
const API_BASE =
  typeof window !== 'undefined' && (window.location.port === '5173' || window.location.port === '3000')
    ? `http://${window.location.hostname}:8000/api/v1`
    : '/api/v1';

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

export async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const fullUrl = url.startsWith('http') ? url : `${API_BASE}${url}`;
  const response = await fetch(fullUrl, {
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
    ...init,
  });

  if (!response.ok) {
    let errorMessage = `API Error ${response.status}: ${response.statusText}`;
    try {
      const errJson = await response.json();
      if (errJson && typeof errJson.detail === 'string') {
        errorMessage = errJson.detail;
      }
    } catch {
      // Keep fallback message
    }
    throw new ApiError(errorMessage, response.status);
  }

  return response.json() as Promise<T>;
}
