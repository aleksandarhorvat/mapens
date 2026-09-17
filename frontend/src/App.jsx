// Placeholder UI so the stack runs end to end. Owner: Person B.
import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import { getEvents, getHealth, USE_MOCK } from './api.js'

const COLORS = { patrol: '#1f5fa8', accident: '#c0392b', jam: '#e67e22' }
const NOVI_SAD = [45.2551, 19.8452]

export default function App() {
  const [events, setEvents] = useState([])
  const [backend, setBackend] = useState('checking...')

  useEffect(() => {
    getHealth().then(() => setBackend('ok')).catch(() => setBackend('unreachable'))
    getEvents().then((d) => setEvents(d.events)).catch(console.error)
  }, [])

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', fontFamily: 'system-ui' }}>
      <header style={{ padding: '8px 12px', borderBottom: '1px solid #ddd' }}>
        <b>MapeNS</b> | backend: {backend} {USE_MOCK && ', mock data'}
      </header>
      <MapContainer center={NOVI_SAD} zoom={13} style={{ flex: 1 }}>
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {events.map((e) => (
          <CircleMarker
            key={e.id}
            center={[e.lat, e.lon]}
            radius={10}
            pathOptions={{
              color: COLORS[e.type],
              fillColor: COLORS[e.type],
              fillOpacity: Math.max(0.15, 1 - e.age_min / e.ttl_min),
            }}
          >
            <Popup>
              <b>{e.type}</b> - {e.location_name}<br />
              {e.report_count} report(s), {e.age_min} min ago
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  )
}
