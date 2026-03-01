import type {
  discussionMessage,
  discussionSession,
  expert,
} from '@/config/db/schema';

// Schema-derived types
export type DiscussionSession = typeof discussionSession.$inferSelect;
export type NewDiscussionSession = typeof discussionSession.$inferInsert;
export type UpdateDiscussionSession = Partial<
  Omit<NewDiscussionSession, 'id' | 'createdAt' | 'topicId' | 'userId'>
>;

export type DiscussionMessage = typeof discussionMessage.$inferSelect;
export type NewDiscussionMessage = typeof discussionMessage.$inferInsert;

export type Expert = typeof expert.$inferSelect;
export type NewExpert = typeof expert.$inferInsert;
export type UpdateExpert = Partial<
  Omit<NewExpert, 'id' | 'createdAt' | 'createdByUserId'>
>;

// Domain enums
export enum SessionStatus {
  INITIALIZING = 'initializing',
  FACT_CHECKING = 'fact_checking',
  DISCUSSING = 'discussing',
  CONCLUDING = 'concluding',
  COMPLETED = 'completed',
}

export enum SessionMode {
  AUTOPILOT = 'autopilot',
  HOST = 'host',
  PARTICIPANT = 'participant',
}

export enum MessageRole {
  EXPERT = 'expert',
  HOST = 'host',
  PARTICIPANT = 'participant',
  SYSTEM = 'system',
  FACT_CHECKER = 'fact_checker',
}

export enum ExpertRole {
  ECONOMIST = 'economist',
  TECHNOLOGIST = 'technologist',
  ETHICIST = 'ethicist',
  FACT_CHECKER = 'fact_checker',
  CUSTOM = 'custom',
}

export enum ExpertStance {
  SUPPORTIVE = 'supportive',
  CRITICAL = 'critical',
  NEUTRAL = 'neutral',
  ANALYTICAL = 'analytical',
}

// Domain interfaces
export interface AutopilotState {
  isActive: boolean;
  currentPhase: SessionStatus;
  nextSpeaker: string | null;
  suggestedAction: string | null;
}

export interface ConsensusState {
  level: number; // 0-100
  agreements: string[];
  disagreements: string[];
  undecided: string[];
}

export interface Citation {
  title: string;
  url: string;
  snippet: string;
  timestamp?: string;
  credibility?: number; // 0-1
}
