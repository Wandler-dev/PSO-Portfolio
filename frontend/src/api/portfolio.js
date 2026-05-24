async function requestJson(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(options.headers || {})
    },
    ...options
  })

  if (!response.ok) {
    let message = `请求失败：${response.status}`
    try {
      const errorBody = await response.json()
      message = errorBody.detail || errorBody.message || message
    } catch {
      // Keep the HTTP status message if the body is not JSON.
    }
    throw new Error(typeof message === 'string' ? message : JSON.stringify(message))
  }

  return response.json()
}

export function fetchHealth() {
  return requestJson('/api/health')
}

export function fetchDataSummary() {
  return requestJson('/api/data/summary')
}

export function fetchPresets() {
  return requestJson('/api/presets')
}

export function runOptimize(payload) {
  return requestJson('/api/optimize', {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}
