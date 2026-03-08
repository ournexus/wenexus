import { notFound } from 'next/navigation';
import { getTopicById } from '@/domains/discovery/services/topic-service';
import { findOrCreateSession } from '@/domains/roundtable/services/chat-service';

import { RoundtableClient } from './roundtable-client';

export default async function RoundtablePage({
  params,
}: {
  params: Promise<{ topicId: string; locale: string }>;
}) {
  const { topicId } = await params;
  const topic = await getTopicById(topicId);

  if (!topic) {
    notFound();
  }

  // Create or find session server-side (no auth needed for dev)
  const session = await findOrCreateSession(topicId, topic.userId);

  return (
    <RoundtableClient
      topic={{
        id: topic.id,
        title: topic.title,
        description: topic.description,
        type: topic.type,
        consensusLevel: topic.consensusLevel ?? 0,
      }}
      sessionId={session.id}
      initialStatus={session.status}
    />
  );
}
