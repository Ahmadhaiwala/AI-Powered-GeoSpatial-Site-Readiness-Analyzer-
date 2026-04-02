import { useEffect, useRef } from 'react'
import * as L from 'leaflet'
import { useMapStore } from '../store'
import { useLocationEval } from '../hooks/useLocationEval'

const markerIcon = L.icon({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

export function MapContainer() {
  const mapRef = useRef<L.Map | null>(null)
  const markersRef = useRef<Map<string, L.Marker>>(new Map())

  const {
    locations,
    selectedLocation,
    mapCenter,
    mapZoom,
    addLocation,
    selectLocation,
    businessType,
  } = useMapStore()
  const { evaluateLocation } = useLocationEval()

  // ── Init map once ─────────────────────────────────────────────────────────
  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map('map', {
        // Prevent Leaflet from stealing pointer events from overlaid React panels
        preferCanvas: false,
      }).setView([mapCenter[0], mapCenter[1]], mapZoom)

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(mapRef.current)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // ── Attach click handler (re-attach when businessType changes) ────────────
  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    const handleClick = async (e: L.LeafletMouseEvent) => {
      const { lat, lng } = e.latlng
      const newLocation = {
        lat,
        lng,
        name: `Pin ${Date.now().toString().slice(-4)}`,
        businessType,
        score: null,
      }
      // Add pin WITHOUT changing selectedLocation (panels stay stable)
      addLocation(newLocation)
      // Then select this pin and evaluate — panels will show its data once scored
      selectLocation(newLocation)
      await evaluateLocation(newLocation)
    }

    map.on('click', handleClick)
    return () => { map.off('click', handleClick) }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [businessType])

  // ── Sync markers when locations list changes ──────────────────────────────
  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    // Remove all old markers
    markersRef.current.forEach((marker) => map.removeLayer(marker))
    markersRef.current.clear()

    // Re-add all markers
    locations.forEach((location) => {
      const isSelected =
        selectedLocation?.lat === location.lat && selectedLocation?.lng === location.lng

      const scoreHtml = location.score
        ? `<div style="margin-top:6px;padding:4px 8px;background:#d1fae5;border-radius:6px">
             <strong style="color:#065f46">Score: ${location.score.score}/100</strong>
           </div>`
        : `<small style="color:#94a3b8">Evaluating…</small>`

      const popupContent = `
        <div style="padding:6px;min-width:140px">
          <strong style="color:#0f172a">${location.name}</strong><br/>
          <small style="color:#64748b">${location.businessType.replace(/_/g, ' ')}</small><br/>
          ${scoreHtml}
        </div>
      `

      const marker = L.marker([location.lat, location.lng], {
        icon: markerIcon,
        title: location.name,
      })
        .bindPopup(popupContent)
        .on('click', () => {
          // Clicking an existing marker selects it (updates panels)
          selectLocation(location)
          marker.openPopup()
        })
        .addTo(map)

      if (isSelected) marker.openPopup()

      markersRef.current.set(`${location.lat}-${location.lng}`, marker)
    })
  }, [locations, selectedLocation])

  return <div id="map" className="w-full h-full" style={{ zIndex: 0 }} />
}
