import { useState } from 'react'
import MapView from './MapView'
import PlacesList from './PlacesList'
import '../styles/SplitView.css'

const SplitView = () => {
  const [mapBounds, setMapBounds] = useState({
    north: 0,
    south: 0,
    east: 0,
    west: 0
  })
  
  // Handle drag to resize
  const [splitPosition, setSplitPosition] = useState(50) // Default to 50%
  const [isDragging, setIsDragging] = useState(false)
  
  const handleMouseDown = () => {
    setIsDragging(true)
  }
  
  const handleMouseUp = () => {
    setIsDragging(false)
  }
  
  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return
    
    const container = e.currentTarget as HTMLDivElement
    const rect = container.getBoundingClientRect()
    const x = e.clientX - rect.left
    const percent = Math.min(Math.max((x / rect.width) * 100, 20), 80)
    
    setSplitPosition(percent)
  }

  const handleBoundsChanged = (bounds: {
    north: number
    south: number
    east: number
    west: number
  }) => {
    setMapBounds(bounds)
  }

  return (
    <div 
      className="split-view-container"
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      <div 
        className="map-panel"
        style={{ width: `${splitPosition}%` }}
      >
        <MapView onBoundsChanged={handleBoundsChanged} />
      </div>
      
      <div 
        className="divider"
        onMouseDown={handleMouseDown}
        data-dragging={isDragging}
      >
        <div className="divider-handle"></div>
      </div>
      
      <div 
        className="list-panel"
        style={{ width: `${100 - splitPosition}%` }}
      >
        <PlacesList mapBounds={mapBounds} />
      </div>
    </div>
  )
}

export default SplitView
