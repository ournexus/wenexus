import { domainEventBus } from '@/domains/shared-kernel';

import { getUuid } from '@/shared/lib/hash';

import {
  createTopicRecord,
  findTopicById as findTopic,
  getTopics,
  updateTopicRecord,
} from '../models/topic';
import {
  TopicVisibility,
  type Topic,
  type TopicCreateInput,
  type TopicStatus,
} from '../types';

export async function createTopic(
  userId: string,
  input: TopicCreateInput
): Promise<Topic> {
  const id = getUuid();
  const record = await createTopicRecord({
    id,
    userId,
    title: input.title,
    description: input.description || null,
    type: input.type,
    status: 'active',
    visibility: input.visibility,
    deliverableType: input.deliverableType || null,
    tags: input.tags || null,
    consensusLevel: 0,
    participantCount: 0,
  });

  await domainEventBus.emit({
    type: 'TOPIC_CREATED',
    payload: {
      topicId: record.id,
      isPrivate: record.visibility === 'private',
      expectedDeliverableType: record.deliverableType ?? undefined,
    },
  });

  return record;
}

export async function getTopicById(id: string): Promise<Topic | null> {
  const result = await findTopic(id);
  return result ?? null;
}

export async function listTopics(params: {
  status?: TopicStatus;
  page?: number;
  limit?: number;
}): Promise<Topic[]> {
  return getTopics({
    status: params.status,
    visibility: TopicVisibility.PUBLIC,
    page: params.page,
    limit: params.limit,
  });
}

export async function updateTopicConsensus(
  topicId: string,
  level: number
): Promise<void> {
  await updateTopicRecord(topicId, { consensusLevel: level });
}
