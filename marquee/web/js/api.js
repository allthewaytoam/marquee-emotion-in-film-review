const API_BASE = window.MARQUEE_API_BASE ?? '/api';

export class ApiError extends Error {
  constructor(message, code, status) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

async function request(path, signal) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, { signal, headers: { Accept: 'application/json' } });
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new ApiError('Cannot reach the server. Check that the backend is running.', 'network', 0);
  }

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(
      body?.error?.message ?? 'The server sent an unexpected response.',
      body?.error?.code ?? 'unknown',
      response.status,
    );
  }
  return body;
}


export const fetchMovies = (query, signal) =>
  request(`/movies?query=${encodeURIComponent(query)}`, signal);

export const fetchAnalysis = (movieId, signal) =>
  request(`/movies/${encodeURIComponent(movieId)}/analysis`, signal);
