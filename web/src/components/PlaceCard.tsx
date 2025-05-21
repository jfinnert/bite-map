import { useState } from 'react'
import '../styles/PlaceCard.css'
import DetailDrawer from './DetailDrawer'

type PlaceCardProps = {
  place: {
    properties: {
      id: number
      name: string
      address: string
      city?: string
      state?: string
      review_count: number
    }
  }
}

const PlaceCard = ({ place }: PlaceCardProps) => {
  const [showDetail, setShowDetail] = useState(false)
  
  const { name, address, city, state, review_count } = place.properties
  
  const handleClick = () => {
    setShowDetail(true)
  }

  return (
    <>
      <div className="place-card" onClick={handleClick}>
        <h3>{name}</h3>
        <p className="address">{address}</p>
        {(city || state) && (
          <p className="location">{[city, state].filter(Boolean).join(', ')}</p>
        )}
        <div className="review-count">
          {review_count} {review_count === 1 ? 'review' : 'reviews'}
        </div>
      </div>
      
      <DetailDrawer 
        placeId={place.properties.id}
        isOpen={showDetail}
        onClose={() => setShowDetail(false)}
      />
    </>
  )
}

export default PlaceCard
