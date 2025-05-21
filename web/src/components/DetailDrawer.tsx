import { useEffect } from 'react'
import { usePlaceDetailQuery } from '../api/places'
import '../styles/DetailDrawer.css'

interface DetailDrawerProps {
  placeId: number
  isOpen: boolean
  onClose: () => void
}

const DetailDrawer = ({ placeId, isOpen, onClose }: DetailDrawerProps) => {
  const { data: place, isLoading, error } = usePlaceDetailQuery(placeId, isOpen)

  // Close drawer with escape key
  useEffect(() => {
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscKey)
    }

    return () => {
      document.removeEventListener('keydown', handleEscKey)
    }
  }, [isOpen, onClose])

  if (!isOpen) {
    return null
  }

  return (
    <div className="drawer-overlay">
      <div className="detail-drawer">
        <button className="close-button" onClick={onClose}>×</button>
        
        <div className="drawer-content">
          {isLoading ? (
            <div className="loading">Loading place details...</div>
          ) : error ? (
            <div className="error">Error loading place details</div>
          ) : place ? (
            <>
              <h2>{place.name}</h2>
              <p className="address">{place.address}</p>
              
              {place.city && place.state && (
                <p className="location">
                  {place.city}, {place.state}
                  {place.country && `, ${place.country}`}
                </p>
              )}
              
              <div className="reviews-section">
                <h3>Videos</h3>
                {place.reviews.length === 0 ? (
                  <p>No videos available for this place.</p>
                ) : (
                  <ul className="review-list">
                    {place.reviews.map((review) => (
                      <li key={review.id} className="review-item">
                        <div className="review-content">
                          <h4>{review.title || 'Food Video'}</h4>
                          <a 
                            href={review.source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="source-link"
                          >
                            View on {review.source.platform === 'youtube' ? 'YouTube' : 'TikTok'}
                          </a>
                        </div>
                        
                        {review.thumbnail_url && (
                          <div className="thumbnail">
                            <img 
                              src={review.thumbnail_url} 
                              alt={review.title || 'Video thumbnail'} 
                            />
                          </div>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </>
          ) : (
            <div className="error">Place not found</div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DetailDrawer
