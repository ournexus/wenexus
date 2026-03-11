/**
 * @module Discovery Domain
 * @description 发现域：信息流、话题管理、观点卡片
 * @depends shared-kernel (Event Bus, LLM Gateway)
 * @consumers Roundtable 域 (via TopicCreated event), App Router pages
 */

// Types
export type {
  Topic,
  NewTopic,
  UpdateTopic,
  ObservationCard,
  FeedCard,
  TopicCreateInput,
} from './types';
export {
  TopicType,
  TopicStatus,
  TopicVisibility,
  ObservationCardStatus,
} from './types';

// Services
export {
  createTopic,
  getTopicById,
  listTopics,
} from './services/topic-service';
export { getFeedCards } from './services/feed-service';
