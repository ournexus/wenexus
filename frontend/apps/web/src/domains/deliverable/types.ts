import type { deliverable } from '@/config/db/schema';

// Schema-derived types
export type Deliverable = typeof deliverable.$inferSelect;
export type NewDeliverable = typeof deliverable.$inferInsert;
export type UpdateDeliverable = Partial<
  Omit<NewDeliverable, 'id' | 'createdAt'>
>;

// Domain enums
export enum DeliverableType {
  REPORT = 'report',
  ARTICLE = 'article',
  SCRIPT = 'script',
  CHECKLIST = 'checklist',
  SOCIAL = 'social',
  OBSERVATION_CARD = 'observation_card',
}

export enum DeliverableStatus {
  GENERATING = 'generating',
  READY = 'ready',
  EXPORTED = 'exported',
  FAILED = 'failed',
}

export enum DeliverableFormat {
  MARKDOWN = 'markdown',
  HTML = 'html',
  JSON = 'json',
  JSX = 'jsx',
}

// Domain interfaces
export interface DeliverableReadiness {
  isReady: boolean;
  readinessScore: number; // 0-100
  missingElements: string[];
  suggestions: string[];
}

export interface DeliverableGenerateInput {
  sessionId: string;
  topicId: string;
  type: DeliverableType;
  format?: DeliverableFormat;
}
