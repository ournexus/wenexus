import { DomainEvent, DomainEventHandler, DomainEventType } from './types';

class DomainEventBus {
  private handlers = new Map<DomainEventType, Set<DomainEventHandler>>();

  on<T extends DomainEvent>(
    eventType: T['type'],
    handler: DomainEventHandler<T>
  ): () => void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
    }
    this.handlers.get(eventType)!.add(handler as DomainEventHandler);

    return () => {
      this.handlers.get(eventType)?.delete(handler as DomainEventHandler);
    };
  }

  async emit<T extends DomainEvent>(event: T): Promise<void> {
    const handlers = this.handlers.get(event.type);
    if (!handlers) return;

    const results = await Promise.allSettled(
      Array.from(handlers).map((handler) => handler(event))
    );

    for (const result of results) {
      if (result.status === 'rejected') {
        console.error('Domain event handler failed:', result.reason);
      }
    }
  }

  clear(): void {
    this.handlers.clear();
  }
}

export const domainEventBus = new DomainEventBus();
