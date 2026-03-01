/**
 * @module Deliverable Domain
 * @description 交付域：内容生成、AIGC 渲染、导出分发
 * @depends shared-kernel (LLM Gateway), Roundtable 域 (via DiscussionReady event)
 * @consumers Discovery 域 (via FeedContentDistilled event), App Router pages
 */

// Types
export type {
  Deliverable,
  NewDeliverable,
  UpdateDeliverable,
  DeliverableReadiness,
  DeliverableGenerateInput,
} from './types';
export { DeliverableType, DeliverableStatus, DeliverableFormat } from './types';

// Services
export {
  generateDeliverable,
  getDeliverableById,
  listDeliverablesBySession,
} from './services/deliverable-service';
export { assessReadiness } from './services/readiness-service';
