import { and, count, desc, eq } from 'drizzle-orm';

import type {
  DiscussionSession,
  NewDiscussionSession,
  UpdateDiscussionSession,
} from '../types';

import { discussionSession } from '@/config/db/schema';
import { db } from '@/core/db';


export async function createSessionRecord(
  data: NewDiscussionSession
): Promise<DiscussionSession> {
  const [result] = await db()
    .insert(discussionSession)
    .values(data)
    .returning();
  return result;
}

export async function findSessionById(
  id: string
): Promise<DiscussionSession | undefined> {
  const [result] = await db()
    .select()
    .from(discussionSession)
    .where(eq(discussionSession.id, id));
  return result;
}

export async function getSessionsByTopic({
  topicId,
  status,
  page = 1,
  limit = 10,
}: {
  topicId: string;
  status?: string;
  page?: number;
  limit?: number;
}): Promise<DiscussionSession[]> {
  return db()
    .select()
    .from(discussionSession)
    .where(
      and(
        eq(discussionSession.topicId, topicId),
        status ? eq(discussionSession.status, status) : undefined
      )
    )
    .orderBy(desc(discussionSession.createdAt))
    .limit(limit)
    .offset((page - 1) * limit);
}

export async function getSessionsByUser({
  userId,
  status,
  page = 1,
  limit = 30,
}: {
  userId: string;
  status?: string;
  page?: number;
  limit?: number;
}): Promise<DiscussionSession[]> {
  return db()
    .select()
    .from(discussionSession)
    .where(
      and(
        eq(discussionSession.userId, userId),
        status ? eq(discussionSession.status, status) : undefined
      )
    )
    .orderBy(desc(discussionSession.createdAt))
    .limit(limit)
    .offset((page - 1) * limit);
}

export async function getSessionsCount({
  topicId,
  userId,
}: {
  topicId?: string;
  userId?: string;
} = {}): Promise<number> {
  const [result] = await db()
    .select({ count: count() })
    .from(discussionSession)
    .where(
      and(
        topicId ? eq(discussionSession.topicId, topicId) : undefined,
        userId ? eq(discussionSession.userId, userId) : undefined
      )
    );
  return result?.count || 0;
}

export async function updateSessionRecord(
  id: string,
  data: UpdateDiscussionSession
): Promise<DiscussionSession> {
  const [result] = await db()
    .update(discussionSession)
    .set(data)
    .where(eq(discussionSession.id, id))
    .returning();
  return result;
}
