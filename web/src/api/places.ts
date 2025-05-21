import { useQuery } from '@tanstack/react-query'

// API base URL from environment variables
const API_URL = import.meta.env.VITE_API_URL || '/api'

// Common types
export interface Place {
  id: number
  name: string
  slug: string
  address: string
  city: string | null
  state: string | null
  country: string | null
  postal_code: string | null
  lat: number
  lng: number
  created_at: string
  updated_at: string | null
}

export interface Review {
  id: number
  title: string | null
  thumbnail_url: string | null
  source: {
    id: number
    url: string
    platform: string
    status: string
    created_at: string
  }
}

export interface PlaceDetail extends Place {
  reviews: Review[]
}

export interface PlacesResponse {
  type: 'FeatureCollection'
  features: Array<{
    type: 'Feature'
    geometry: {
      type: 'Point'
      coordinates: [number, number] // [longitude, latitude]
    }
    properties: {
      id: number
      name: string
      address: string
      slug: string
      city: string | null
      state: string | null
      country: string | null
      review_count: number
    }
  }>
  metadata: {
    total: number
    limit: number
    offset: number
    page: number
    pages: number
  }
}

// Fetch places with optional filtering
export const fetchPlaces = async (
  params: { 
    bbox?: string
    q?: string
    limit?: number
    offset?: number
  } = {}
): Promise<PlacesResponse> => {
  const queryParams = new URLSearchParams()
  
  if (params.bbox) queryParams.append('bbox', params.bbox)
  if (params.q) queryParams.append('q', params.q)
  if (params.limit) queryParams.append('limit', params.limit.toString())
  if (params.offset) queryParams.append('offset', params.offset.toString())
  
  const queryString = queryParams.toString()
  const url = `${API_URL}/places${queryString ? `?${queryString}` : ''}`
  
  const response = await fetch(url)
  
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`)
  }
  
  return response.json()
}

// Fetch a single place by ID
export const fetchPlaceById = async (id: number): Promise<PlaceDetail> => {
  const response = await fetch(`${API_URL}/places/${id}`)
  
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`)
  }
  
  return response.json()
}

// React Query hook for places
export const usePlacesQuery = (params: {
  bbox?: string
  q?: string
  limit?: number
  offset?: number
}) => {
  return useQuery({
    queryKey: ['places', params],
    queryFn: () => fetchPlaces(params),
    enabled: !!params.bbox || !!params.q, // Only fetch if we have bounds or search
  })
}

// React Query hook for place details
export const usePlaceDetailQuery = (id: number, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['place', id],
    queryFn: () => fetchPlaceById(id),
    enabled: enabled && !!id, // Only fetch if enabled and id exists
  })
}
