import { getUuid } from '@/shared/lib/hash';

import {
  createMessageRecord,
  getMessagesBySession,
} from '../models/discussion-message';
import {
  createSessionRecord,
  findSessionById,
  getSessionsByTopic,
  updateSessionRecord,
} from '../models/discussion-session';
import type {
  DiscussionMessage,
  DiscussionSession,
  NewDiscussionMessage,
  NewDiscussionSession,
} from '../types';
import { getBuiltinExperts } from './expert-service';

export async function createSession(
  input: Omit<NewDiscussionSession, 'id' | 'createdAt' | 'updatedAt'>
): Promise<DiscussionSession> {
  const id = getUuid();
  const builtinExperts = await getBuiltinExperts();
  const expertIds = builtinExperts.map((e) => e.id);

  return createSessionRecord({
    id,
    ...input,
    expertIds: expertIds,
  });
}

export async function getSessionById(
  sessionId: string
): Promise<DiscussionSession | null> {
  const result = await findSessionById(sessionId);
  return result ?? null;
}

export async function findOrCreateSession(
  topicId: string,
  userId: string
): Promise<DiscussionSession> {
  const existing = await getSessionsByTopic({ topicId, page: 1, limit: 1 });
  const userSession = existing.find((s) => s.userId === userId);
  if (userSession) return userSession;

  return createSession({
    topicId,
    userId,
    status: 'initializing',
    mode: 'autopilot',
    isPrivate: false,
  });
}

export async function getSessionMessages(
  sessionId: string,
  params?: { page?: number; limit?: number }
): Promise<DiscussionMessage[]> {
  const messages = await getMessagesBySession({
    sessionId,
    page: params?.page || 1,
    limit: params?.limit || 100,
  });
  return messages.reverse();
}

export async function addMessage(
  sessionId: string,
  message: Omit<
    NewDiscussionMessage,
    'id' | 'sessionId' | 'createdAt' | 'updatedAt'
  >
): Promise<DiscussionMessage> {
  const id = getUuid();
  return createMessageRecord({
    id,
    sessionId,
    ...message,
  });
}

export async function updateSession(
  sessionId: string,
  data: Partial<DiscussionSession>
): Promise<DiscussionSession> {
  return updateSessionRecord(sessionId, data);
}

export interface SendMessageResult {
  userMessage: DiscussionMessage;
  aiReplies: DiscussionMessage[];
  status: 'success' | 'pending';
  sessionId: string;
}

export async function sendMessage(
  sessionId: string,
  content: string,
  generateAiReply: boolean = true
): Promise<SendMessageResult> {
  const response = await fetch('/api/domains/roundtable/messages/send', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      sessionId,
      content,
      generateAiReply,
    }),
  });

  const data = await response.json();

  if (data.code !== 0) {
    throw new Error(data.message || 'Failed to send message');
  }

  return data.data as SendMessageResult;
}
