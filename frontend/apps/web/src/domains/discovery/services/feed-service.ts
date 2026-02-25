import { getExperts } from '@/domains/roundtable/models/expert';

import { getObservationCardsByTopic } from '../models/observation-card';
import { getTopics } from '../models/topic';
import type { FeedCard } from '../types';

export async function getFeedCards(params: {
  page?: number;
  limit?: number;
}): Promise<FeedCard[]> {
  const topics = await getTopics({
    visibility: 'public',
    page: params.page || 1,
    limit: params.limit || 20,
  });

  const feedCards: FeedCard[] = await Promise.all(
    topics.map(async (topic) => {
      const observationCards = await getObservationCardsByTopic({
        topicId: topic.id,
        status: 'active',
        limit: 3,
      });

      const expertCount = (
        await getExperts({ isBuiltin: true, status: 'active' })
      ).length;

      return {
        topic,
        observationCards,
        expertCount,
        consensusLevel: topic.consensusLevel ?? 0,
      };
    })
  );

  return feedCards;
}
