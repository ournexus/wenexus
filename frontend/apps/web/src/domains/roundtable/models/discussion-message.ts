import { and, count, desc, eq } from 'drizzle-orm';

import { db } from '@/core/db';
import { discussionMessage } from '@/config/db/schema';

import type { DiscussionMessage, NewDiscussionMessage } from '../types';

export async function createMessageRecord(
  data: NewDiscussionMessage
): Promise<DiscussionMessage> {
  const [result] = await db()
    .insert(discussionMessage)
    .values(data)
    .returning();
  return result;
}

export async function findMessageById(
  id: string
): Promise<DiscussionMessage | undefined> {
  const [result] = await db()
    .select()
    .from(discussionMessage)
    .where(eq(discussionMessage.id, id));
  return result;
}

export async function getMessagesBySession({
  sessionId,
  page = 1,
  limit = 100,
}: {
  sessionId: string;
  page?: number;
  limit?: number;
}): Promise<DiscussionMessage[]> {
  return db()
    .select()
    .from(discussionMessage)
    .where(eq(discussionMessage.sessionId, sessionId))
    .orderBy(desc(discussionMessage.createdAt))
    .limit(limit)
    .offset((page - 1) * limit);
}

export async function getMessagesByThread({
  threadRef,
}: {
  threadRef: string;
}): Promise<DiscussionMessage[]> {
  return db()
    .select()
    .from(discussionMessage)
    .where(eq(discussionMessage.threadRef, threadRef))
    .orderBy(desc(discussionMessage.createdAt));
}

export async function getMessagesCount({
  sessionId,
}: {
  sessionId: string;
}): Promise<number> {
  const [result] = await db()
    .select({ count: count() })
    .from(discussionMessage)
    .where(eq(discussionMessage.sessionId, sessionId));
  return result?.count || 0;
}
