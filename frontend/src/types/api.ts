export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface UserResponse {
  id: string
  username: string
  email: string
  avatar_url: string | null
  role: string
  elo_rating: number
  is_active: boolean
  created_at: string
}
