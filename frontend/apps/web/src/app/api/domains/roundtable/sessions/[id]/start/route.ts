import { getTopicById } from '@/domains/discovery/services/topic-service';
import { getSessionById } from '@/domains/roundtable/services/chat-service';
import { startDiscussion } from '@/domains/roundtable/services/discussion-orchestrator';

import { respData, respErr } from '@/shared/lib/resp';

export async function POST(
  _req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: sessionId } = await params;

    const session = await getSessionById(sessionId);
    if (!session) {
      return respErr('Session not found', 1, 404);
    }

    const topic = await getTopicById(session.topicId);
    if (!topic) {
      return respErr('Topic not found', 1, 404);
    }

    const message = await startDiscussion(
      sessionId,
      topic.title,
      topic.description ?? undefined
    );

    return respData(message);
  } catch (e: any) {
    console.error('start discussion failed:', e);
    return respErr(e.message || 'start discussion failed');
  }
}
