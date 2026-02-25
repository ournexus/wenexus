import {
  addMessage,
  getSessionMessages,
} from '@/domains/roundtable/services/chat-service';

import { respData, respErr } from '@/shared/lib/resp';

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const sessionId = searchParams.get('sessionId');
    if (!sessionId) {
      return respErr('sessionId is required');
    }

    const messages = await getSessionMessages(sessionId);
    return respData({ messages, total: messages.length });
  } catch (e: any) {
    console.error('list messages failed:', e);
    return respErr(e.message || 'list messages failed');
  }
}

export async function POST(req: Request) {
  try {
    const { sessionId, role, content, expertId, threadRef } = await req.json();
    if (!sessionId || !role || !content) {
      return respErr('sessionId, role, and content are required');
    }

    const message = await addMessage(sessionId, {
      role,
      content,
      expertId: expertId || null,
      threadRef: threadRef || null,
      status: 'active',
    });

    return respData(message);
  } catch (e: any) {
    console.error('create message failed:', e);
    return respErr(e.message || 'create message failed');
  }
}
