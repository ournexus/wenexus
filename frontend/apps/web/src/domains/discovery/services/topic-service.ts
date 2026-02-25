import type { Topic, TopicCreateInput, TopicStatus } from '../types';

export async function createTopic(
  _userId: string,
  _input: TopicCreateInput
): Promise<Topic> {
  // 1. Validate input
  // 2. Create topic record
  // 3. Emit TOPIC_CREATED event via domainEventBus
  throw new Error('Not implemented');
}

export async function getTopicById(_id: string): Promise<Topic | null> {
  throw new Error('Not implemented');
}

export async function listTopics(_params: {
  status?: TopicStatus;
  page?: number;
  limit?: number;
}): Promise<Topic[]> {
  throw new Error('Not implemented');
}

export async function updateTopicConsensus(
  _topicId: string,
  _level: number
): Promise<void> {
  throw new Error('Not implemented');
}
