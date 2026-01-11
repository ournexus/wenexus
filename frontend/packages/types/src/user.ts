/**
 * User-related type definitions
 */

export interface User {
  id: string;
  email: string;
  username: string;
  displayName: string;
  avatarUrl?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface UserProfile extends User {
  bio?: string;
  location?: string;
  website?: string;
}

export type UserRole = 'user' | 'moderator' | 'admin';

export interface AuthUser {
  user: User;
  token: string;
  refreshToken: string;
  expiresAt: Date;
}
