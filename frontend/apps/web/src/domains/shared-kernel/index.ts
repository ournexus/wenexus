/**
 * @module Shared Kernel
 * @description 跨域共享内核：事件总线、LLM 网关、共享类型
 * @depends 无外部依赖
 * @consumers Discovery, Roundtable, Deliverable, Identity 域
 */

export { domainEventBus } from './event-bus';
export type {
  DomainEvent,
  DomainEventType,
  DomainEventHandler,
} from './event-bus';
export type {
  LLMGateway,
  LLMGenerateOptions,
  LLMResponse,
  LLMStreamChunk,
} from './llm-gateway';
