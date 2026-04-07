export function getApiErrorMessage(error, fallback = 'Request failed') {
  const detail = error?.response?.data?.detail;

  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }

  if (Array.isArray(detail)) {
    const first = detail[0];
    if (typeof first === 'string') return first;
    if (first?.msg) return first.msg;
  }

  if (typeof error?.message === 'string' && error.message.includes('Network Error')) {
    return 'Cannot connect to server. Make sure backend is running on port 8000.';
  }

  if (typeof error?.message === 'string' && error.message.trim()) {
    return error.message;
  }

  if (typeof error?.code === 'string' && error.code === 'ECONNABORTED') {
    return 'Request timed out. Please try again.';
  }

  return fallback;
}
