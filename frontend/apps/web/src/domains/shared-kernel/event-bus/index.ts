/**
 * @module Event Bus
 * @description 领域事件总线，支持跨域异步通信
 * @depends 无
 * @consumers Discovery, Roundtable, Deliverable, Identity 域
 */

export { domainEventBus } from './event-bus';
export type {
  DomainEvent,
  DomainEventType,
  DomainEventHandler,
} from './types';
