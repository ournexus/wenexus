import { getSessionsByTopic } from '@/domains/roundtable/models/discussion-session';
import { findOrCreateSession } from '@/domains/roundtable/services/chat-service';

import { respData, respErr } from '@/shared/lib/resp';
import { getUserInfo } from '@/shared/models/user';

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const topicId = searchParams.get('topicId');

    if (topicId) {
      const sessions = await getSessionsByTopic({ topicId });
      return respData({ sessions, total: sessions.length });
    }

    return respData({ sessions: [], total: 0 });
  } catch (e: any) {
    console.error('list sessions failed:', e);
    return respErr(e.message || 'list sessions failed');
  }
}

export async function POST(req: Request) {
  try {
    const user = await getUserInfo();
    if (!user) {
      return respErr('Please sign in first', 1, 401);
    }

    const { topicId } = await req.json();
    if (!topicId) {
      return respErr('topicId is required');
    }

    const session = await findOrCreateSession(topicId, user.id);
    return respData(session);
  } catch (e: any) {
    console.error('create session failed:', e);
    return respErr(e.message || 'create session failed');
  }
}
