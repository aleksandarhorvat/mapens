// API client. Contract: MAPENS_CONTEXT.md section 6.6. Owner: Person B.
// Set USE_MOCK = false once the backend endpoints are implemented.
import mockEvents from './mock/events.json'

export const USE_MOCK = true
const BASE = '/api'

async function request(path, options) {
  const res = await fetch(`${BASE}${path}`, options)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} on ${path}`)
  return res.json()
}

export const getHealth = () => request('/health')

export const getEvents = async (params = {}) => {
  if (USE_MOCK) return mockEvents
  return request(`/events?${new URLSearchParams(params)}`)
}

// TODO(B): getEventMessages, search, getUnresolved, replayStart/Pause/Status, ingest
