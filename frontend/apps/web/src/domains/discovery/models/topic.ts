import { and, count, desc, eq } from 'drizzle-orm';

import type { NewTopic, Topic, TopicStatus, UpdateTopic } from '../types';

import { topic } from '@/config/db/schema';
import { db } from '@/core/db';


export async function createTopicRecord(newTopic: NewTopic): Promise<Topic> {
  const [result] = await db().insert(topic).values(newTopic).returning();
  return result;
}

export async function findTopicById(id: string): Promise<Topic | undefined> {
  const [result] = await db().select().from(topic).where(eq(topic.id, id));
  return result;
}

export async function getTopics({
  userId,
  status,
  visibility,
  page = 1,
  limit = 30,
}: {
  userId?: string;
  status?: TopicStatus;
  visibility?: string;
  page?: number;
  limit?: number;
} = {}): Promise<Topic[]> {
  return db()
    .select()
    .from(topic)
    .where(
      and(
        userId ? eq(topic.userId, userId) : undefined,
        status ? eq(topic.status, status) : undefined,
        visibility ? eq(topic.visibility, visibility) : undefined
      )
    )
    .orderBy(desc(topic.createdAt))
    .limit(limit)
    .offset((page - 1) * limit);
}

export async function getTopicsCount({
  userId,
  status,
}: {
  userId?: string;
  status?: TopicStatus;
} = {}): Promise<number> {
  const [result] = await db()
    .select({ count: count() })
    .from(topic)
    .where(
      and(
        userId ? eq(topic.userId, userId) : undefined,
        status ? eq(topic.status, status) : undefined
      )
    );
  return result?.count || 0;
}

export async function updateTopicRecord(
  id: string,
  data: UpdateTopic
): Promise<Topic> {
  const [result] = await db()
    .update(topic)
    .set(data)
    .where(eq(topic.id, id))
    .returning();
  return result;
}
