import { useState, useEffect } from 'react'
import { usePlacesQuery } from '../api/places'
import PlaceCard from './PlaceCard'
import '../styles/PlacesList.css'

type PlacesListProps = {
  mapBounds?: {
    north: number
    south: number
    east: number
    west: number
  }
}

const PlacesList = ({ mapBounds }: PlacesListProps) => {
  const [searchQuery, setSearchQuery] = useState('')

  // Convert bounds to bbox string parameter
  const bbox = mapBounds 
    ? `${mapBounds.west},${mapBounds.south},${mapBounds.east},${mapBounds.north}` 
    : undefined

  // Fetch places based on bounds and search query
  const { 
    data, 
    isLoading, 
    isError,
    refetch 
  } = usePlacesQuery({ bbox, q: searchQuery })

  // Refetch when bounds change
  useEffect(() => {
    if (mapBounds && mapBounds.north !== 0) {
      refetch()
    }
  }, [mapBounds, refetch])

  const places = data?.features || []
  const total = data?.metadata?.total || 0

  return (
    <div className="places-list">
      <div className="places-header">
        <h2>Places</h2>
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search places..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button onClick={() => refetch()}>Search</button>
        </div>
        <div className="places-count">
          {isLoading ? 'Loading...' : `${total} places found`}
        </div>
      </div>

      <div className="places-grid">
        {isLoading ? (
          <div className="loading">Loading places...</div>
        ) : isError ? (
          <div className="error">Error loading places. Please try again.</div>
        ) : places.length === 0 ? (
          <div className="empty">No places found in this area.</div>
        ) : (
          places.map((place) => (
            <PlaceCard key={place.properties.id} place={place} />
          ))
        )}
      </div>
    </div>
  )
}

export default PlacesList
