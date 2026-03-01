/**
 * Domain event types for cross-domain communication.
 * Defined in domain-architecture.md section 5.1.
 */

export type DomainEvent =
  // Discovery -> Roundtable
  | {
      type: 'TOPIC_CREATED';
      payload: {
        topicId: string;
        isPrivate: boolean;
        expectedDeliverableType?: string;
      };
    }
  // Discovery -> Identity
  | { type: 'TOPIC_CLICKED'; payload: { topicId: string; userId: string } }
  // Discovery -> Identity
  | { type: 'CARD_LIKED'; payload: { cardId: string; userId: string } }
  // Roundtable -> Discovery
  | { type: 'CONSENSUS_UPDATED'; payload: { topicId: string; level: number } }
  // Roundtable -> Deliverable
  | {
      type: 'DISCUSSION_READY';
      payload: { topicId: string; sessionId: string; readiness: number };
    }
  // Roundtable -> Identity
  | {
      type: 'EXPERT_SPOKE';
      payload: { expertId: string; sessionId: string; userId: string };
    }
  // Deliverable -> Discovery
  | {
      type: 'FEED_CONTENT_DISTILLED';
      payload: { topicId: string; cards: string[]; summary?: string };
    }
  // Deliverable -> Discovery
  | {
      type: 'DELIVERABLE_GENERATED';
      payload: {
        topicId: string;
        deliverableType: string;
        deliverableId: string;
      };
    }
  // Deliverable -> Identity
  | {
      type: 'DELIVERABLE_EXPORTED';
      payload: { deliverableId: string; userId: string; format: string };
    }
  // Any -> Identity
  | {
      type: 'USER_ACTION';
      payload: { action: string; context: Record<string, unknown> };
    };

export type DomainEventType = DomainEvent['type'];

export type DomainEventHandler<T extends DomainEvent = DomainEvent> = (
  event: T
) => void | Promise<void>;
