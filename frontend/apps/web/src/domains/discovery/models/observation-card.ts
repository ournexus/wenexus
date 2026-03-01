import { and, count, desc, eq } from 'drizzle-orm';

import type {
  NewObservationCard,
  ObservationCard,
  UpdateObservationCard,
} from '../types';

import { observationCard } from '@/config/db/schema';
import { db } from '@/core/db';


export async function createObservationCardRecord(
  data: NewObservationCard
): Promise<ObservationCard> {
  const [result] = await db()
    .insert(observationCard)
    .values(data)
    .returning();
  return result;
}

export async function findObservationCardById(
  id: string
): Promise<ObservationCard | undefined> {
  const [result] = await db()
    .select()
    .from(observationCard)
    .where(eq(observationCard.id, id));
  return result;
}

export async function getObservationCardsByTopic({
  topicId,
  status,
  page = 1,
  limit = 30,
}: {
  topicId: string;
  status?: string;
  page?: number;
  limit?: number;
}): Promise<ObservationCard[]> {
  return db()
    .select()
    .from(observationCard)
    .where(
      and(
        eq(observationCard.topicId, topicId),
        status ? eq(observationCard.status, status) : undefined
      )
    )
    .orderBy(desc(observationCard.createdAt))
    .limit(limit)
    .offset((page - 1) * limit);
}

export async function getObservationCardsCount({
  topicId,
}: {
  topicId: string;
}): Promise<number> {
  const [result] = await db()
    .select({ count: count() })
    .from(observationCard)
    .where(eq(observationCard.topicId, topicId));
  return result?.count || 0;
}

export async function updateObservationCardRecord(
  id: string,
  data: UpdateObservationCard
): Promise<ObservationCard> {
  const [result] = await db()
    .update(observationCard)
    .set(data)
    .where(eq(observationCard.id, id))
    .returning();
  return result;
}
