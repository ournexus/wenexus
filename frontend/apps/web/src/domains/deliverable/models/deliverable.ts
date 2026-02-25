import { and, count, desc, eq } from 'drizzle-orm';

import type { Deliverable, NewDeliverable, UpdateDeliverable } from '../types';

import { deliverable } from '@/config/db/schema';
import { db } from '@/core/db';


export async function createDeliverableRecord(
  data: NewDeliverable
): Promise<Deliverable> {
  const [result] = await db()
    .insert(deliverable)
    .values(data)
    .returning();
  return result;
}

export async function findDeliverableById(
  id: string
): Promise<Deliverable | undefined> {
  const [result] = await db()
    .select()
    .from(deliverable)
    .where(eq(deliverable.id, id));
  return result;
}

export async function getDeliverablesBySession({
  sessionId,
  type,
  page = 1,
  limit = 30,
}: {
  sessionId: string;
  type?: string;
  page?: number;
  limit?: number;
}): Promise<Deliverable[]> {
  return db()
    .select()
    .from(deliverable)
    .where(
      and(
        eq(deliverable.sessionId, sessionId),
        type ? eq(deliverable.type, type) : undefined
      )
    )
    .orderBy(desc(deliverable.createdAt))
    .limit(limit)
    .offset((page - 1) * limit);
}

export async function getDeliverablesByUser({
  userId,
  type,
  status,
  page = 1,
  limit = 30,
}: {
  userId: string;
  type?: string;
  status?: string;
  page?: number;
  limit?: number;
}): Promise<Deliverable[]> {
  return db()
    .select()
    .from(deliverable)
    .where(
      and(
        eq(deliverable.userId, userId),
        type ? eq(deliverable.type, type) : undefined,
        status ? eq(deliverable.status, status) : undefined
      )
    )
    .orderBy(desc(deliverable.createdAt))
    .limit(limit)
    .offset((page - 1) * limit);
}

export async function getDeliverablesCount({
  sessionId,
  userId,
}: {
  sessionId?: string;
  userId?: string;
} = {}): Promise<number> {
  const [result] = await db()
    .select({ count: count() })
    .from(deliverable)
    .where(
      and(
        sessionId ? eq(deliverable.sessionId, sessionId) : undefined,
        userId ? eq(deliverable.userId, userId) : undefined
      )
    );
  return result?.count || 0;
}

export async function updateDeliverableRecord(
  id: string,
  data: UpdateDeliverable
): Promise<Deliverable> {
  const [result] = await db()
    .update(deliverable)
    .set(data)
    .where(eq(deliverable.id, id))
    .returning();
  return result;
}
