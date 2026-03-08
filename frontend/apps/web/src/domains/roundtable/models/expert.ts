import { and, count, desc, eq } from 'drizzle-orm';

import { db } from '@/core/db';
import { expert } from '@/config/db/schema';

import {
  ExpertRole,
  type Expert,
  type NewExpert,
  type UpdateExpert,
} from '../types';

export async function createExpertRecord(data: NewExpert): Promise<Expert> {
  const [result] = await db().insert(expert).values(data).returning();
  return result;
}

export async function findExpertById(id: string): Promise<Expert | undefined> {
  const [result] = await db().select().from(expert).where(eq(expert.id, id));
  return result;
}

export async function getExperts({
  role,
  isBuiltin,
  status,
  page = 1,
  limit = 50,
}: {
  role?: ExpertRole;
  isBuiltin?: boolean;
  status?: string;
  page?: number;
  limit?: number;
} = {}): Promise<Expert[]> {
  return db()
    .select()
    .from(expert)
    .where(
      and(
        role ? eq(expert.role, role) : undefined,
        isBuiltin !== undefined ? eq(expert.isBuiltin, isBuiltin) : undefined,
        status ? eq(expert.status, status) : undefined
      )
    )
    .orderBy(desc(expert.createdAt))
    .limit(limit)
    .offset((page - 1) * limit);
}

export async function getExpertsCount({
  role,
  isBuiltin,
}: {
  role?: ExpertRole;
  isBuiltin?: boolean;
} = {}): Promise<number> {
  const [result] = await db()
    .select({ count: count() })
    .from(expert)
    .where(
      and(
        role ? eq(expert.role, role) : undefined,
        isBuiltin !== undefined ? eq(expert.isBuiltin, isBuiltin) : undefined
      )
    );
  return result?.count || 0;
}

export async function updateExpertRecord(
  id: string,
  data: UpdateExpert
): Promise<Expert> {
  const [result] = await db()
    .update(expert)
    .set(data)
    .where(eq(expert.id, id))
    .returning();
  return result;
}
