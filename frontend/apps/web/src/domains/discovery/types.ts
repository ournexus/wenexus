import type { topic, observationCard } from '@/config/db/schema';

// Schema-derived types
export type Topic = typeof topic.$inferSelect;
export type NewTopic = typeof topic.$inferInsert;
export type UpdateTopic = Partial<Omit<NewTopic, 'id' | 'createdAt'>>;

export type ObservationCard = typeof observationCard.$inferSelect;
export type NewObservationCard = typeof observationCard.$inferInsert;
export type UpdateObservationCard = Partial<
  Omit<NewObservationCard, 'id' | 'createdAt'>
>;

// Domain enums
export enum TopicType {
  DEBATE = 'debate',
  BRAINSTORM = 'brainstorm',
  ANALYSIS = 'analysis',
  EXPLORATION = 'exploration',
}

export enum TopicStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  DISCUSSING = 'discussing',
  COMPLETED = 'completed',
  ARCHIVED = 'archived',
}

export enum TopicVisibility {
  PUBLIC = 'public',
  PRIVATE = 'private',
}

export enum ObservationCardStatus {
  ACTIVE = 'active',
  ARCHIVED = 'archived',
}

// Domain interfaces
export interface FeedCard {
  topic: Topic;
  observationCards: ObservationCard[];
  expertCount: number;
  consensusLevel: number;
}

export interface TopicCreateInput {
  title: string;
  description?: string;
  type: TopicType;
  visibility: TopicVisibility;
  deliverableType?: string;
  tags?: string[];
}
