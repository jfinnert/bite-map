import { useRef, useEffect, useState } from 'react'
import mapboxgl from 'mapbox-gl'
import { usePlacesQuery } from '../api/places'
import 'mapbox-gl/dist/mapbox-gl.css'
import '../styles/MapView.css'

// Mapbox token from environment variables
mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN || ''

type MapViewProps = {
  onBoundsChanged?: (bounds: {
    north: number
    south: number
    east: number
    west: number
  }) => void
}

const MapView = ({ onBoundsChanged }: MapViewProps) => {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const [map, setMap] = useState<mapboxgl.Map | null>(null)
  const [mapBounds, setMapBounds] = useState<string | undefined>()
  const markersRef = useRef<Record<number, mapboxgl.Marker>>({})
  const popupsRef = useRef<Record<number, mapboxgl.Popup>>({})

  // Fetch places based on map bounds
  const { data: places } = usePlacesQuery({
    bbox: mapBounds,
  })

  // Initialize map when component mounts
  useEffect(() => {
    if (!mapContainerRef.current) return

    const mapInstance = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: 'mapbox://styles/mapbox/streets-v11',
      center: [-74.0060, 40.7128], // New York City
      zoom: 12
    })

    // Add navigation control (zoom buttons)
    mapInstance.addControl(new mapboxgl.NavigationControl(), 'top-right')

    // Setup map event listeners
    mapInstance.on('load', () => {
      console.log('Map loaded successfully')
      
      // Set initial bounds to trigger first data load
      const initialBounds = mapInstance.getBounds()
      if (initialBounds) {
        const bbox = `${initialBounds.getWest()},${initialBounds.getSouth()},${initialBounds.getEast()},${initialBounds.getNorth()}`
        setMapBounds(bbox)
      }
    })

    // Update bounds when map moves
    mapInstance.on('moveend', () => {
      const currentBounds = mapInstance.getBounds()
      if (currentBounds) {
        const bbox = `${currentBounds.getWest()},${currentBounds.getSouth()},${currentBounds.getEast()},${currentBounds.getNorth()}`
        setMapBounds(bbox)
        
        if (onBoundsChanged) {
          onBoundsChanged({
            north: currentBounds.getNorth(),
            south: currentBounds.getSouth(),
            east: currentBounds.getEast(),
            west: currentBounds.getWest()
          })
        }
      }
    })

    // Save the map instance
    setMap(mapInstance)

    // Clean up on unmount
    return () => {
      Object.values(markersRef.current).forEach(marker => marker.remove())
      Object.values(popupsRef.current).forEach(popup => popup.remove())
      mapInstance.remove()
    }
  }, [onBoundsChanged])

  // Update markers when places data changes
  useEffect(() => {
    if (!map || !places) return
    
    // Track existing markers to identify ones to remove
    const existingMarkerIds = Object.keys(markersRef.current).map(Number)
    const newMarkerIds: number[] = []
    
    // Add/update markers for each place
    places.features.forEach((feature) => {
      const id = feature.properties.id
      newMarkerIds.push(id)
      
      const [lng, lat] = feature.geometry.coordinates
      const name = feature.properties.name
      const address = feature.properties.address
      const reviewCount = feature.properties.review_count
      
      // Create HTML for popup
      const popupHtml = `
        <div class="map-popup">
          <h3>${name}</h3>
          <p>${address}</p>
          <p>${reviewCount} ${reviewCount === 1 ? 'review' : 'reviews'}</p>
          <a href="#/place/${id}" class="popup-link">View details</a>
        </div>
      `
      
      // Create or update marker
      if (!markersRef.current[id]) {
        // Create popup
        const popup = new mapboxgl.Popup({ offset: 25 })
          .setHTML(popupHtml)
        
        // Create marker
        const marker = new mapboxgl.Marker({ color: '#FF5A5F' })
          .setLngLat([lng, lat])
          .setPopup(popup)
          .addTo(map)
        
        // Store references
        markersRef.current[id] = marker
        popupsRef.current[id] = popup
      } else {
        // Update existing marker
        markersRef.current[id].setLngLat([lng, lat])
        popupsRef.current[id].setHTML(popupHtml)
      }
    })
    
    // Remove markers that are no longer in the data
    existingMarkerIds.forEach(id => {
      if (!newMarkerIds.includes(id)) {
        markersRef.current[id].remove()
        delete markersRef.current[id]
        
        if (popupsRef.current[id]) {
          popupsRef.current[id].remove()
          delete popupsRef.current[id]
        }
      }
    })
  }, [places, map])
  
  return <div className="map-container" ref={mapContainerRef} />
}

export default MapView
