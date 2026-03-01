import type { userPreference } from '@/config/db/schema';

// Schema-derived types
export type UserPreference = typeof userPreference.$inferSelect;
export type NewUserPreference = typeof userPreference.$inferInsert;
export type UpdateUserPreference = Partial<
  Omit<NewUserPreference, 'id' | 'createdAt' | 'userId'>
>;

// Domain enums
export enum DiscussionDepth {
  QUICK = 'quick',
  BALANCED = 'balanced',
  DEEP = 'deep',
}

// Domain interfaces
export interface UserBackgroundInfo {
  profession?: string;
  interests?: string[];
  expertiseLevel?: 'beginner' | 'intermediate' | 'expert';
  preferredLanguage?: string;
}

export interface UserIdentity {
  userId: string;
  backgroundInfo: UserBackgroundInfo;
  preferences: UserPreference;
  isOnboarded: boolean;
}
