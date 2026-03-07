import { getTopicById } from '@/domains/discovery/services/topic-service';
import {
  getSessionById,
  getSessionMessages,
} from '@/domains/roundtable/services/chat-service';
import {
  generateExpertResponse,
  pickNextSpeaker,
} from '@/domains/roundtable/services/discussion-orchestrator';
import { getExpertsForSession } from '@/domains/roundtable/services/expert-service';

import { respData, respErr } from '@/shared/lib/resp';

export async function POST(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: sessionId } = await params;
    const body = await req.json().catch(() => ({}));

    const session = await getSessionById(sessionId);
    if (!session) {
      return respErr('Session not found', 1, 404);
    }

    const topic = await getTopicById(session.topicId);
    if (!topic) {
      return respErr('Topic not found', 1, 404);
    }

    // Determine which expert speaks next
    let expertId = body.expertId;
    if (!expertId) {
      const messages = await getSessionMessages(sessionId);
      const experts = await getExpertsForSession(sessionId);
      const nextExpert = pickNextSpeaker(messages, experts);
      if (!nextExpert) {
        return respErr('No available expert to speak');
      }
      expertId = nextExpert.id;
    }

    const message = await generateExpertResponse(
      sessionId,
      expertId,
      { title: topic.title, description: topic.description ?? undefined },
      body.replyTo
    );

    return respData(message);
  } catch (e: any) {
    console.error('next turn failed:', e);
    return respErr(e.message || 'next turn failed');
  }
}
