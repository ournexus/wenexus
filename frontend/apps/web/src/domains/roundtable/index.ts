/**
 * @module Roundtable Domain
 * @description 圆桌域：AI 专家讨论、线程对话、挂机/接管模式
 * @depends shared-kernel (Event Bus, LLM Gateway)
 * @consumers Discovery 域 (via ConsensusUpdated), Deliverable 域 (via DiscussionReady)
 */

// Types
export type {
  DiscussionSession,
  DiscussionMessage,
  Expert,
  AutopilotState,
  ConsensusState,
  Citation,
} from './types';
export {
  SessionStatus,
  SessionMode,
  MessageRole,
  ExpertRole,
  ExpertStance,
} from './types';

// Services
export {
  getBuiltinExperts,
  createCustomExpert,
  getExpertsForSession,
} from './services/expert-service';
export {
  createSession,
  getSessionMessages,
  addMessage,
} from './services/chat-service';
export { getAutopilotState, switchMode } from './services/autopilot-service';
export { calculateConsensus } from './services/consensus-service';
