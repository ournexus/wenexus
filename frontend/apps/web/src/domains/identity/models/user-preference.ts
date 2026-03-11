import { and, eq } from 'drizzle-orm';

import { db } from '@/core/db';
import { userPreference } from '@/config/db/schema';

import type {
  NewUserPreference,
  UpdateUserPreference,
  UserPreference,
} from '../types';

export async function createUserPreferenceRecord(
  data: NewUserPreference
): Promise<UserPreference> {
  const [result] = await db().insert(userPreference).values(data).returning();
  return result;
}

export async function findUserPreferenceByUserId(
  userId: string
): Promise<UserPreference | undefined> {
  const [result] = await db()
    .select()
    .from(userPreference)
    .where(eq(userPreference.userId, userId));
  return result;
}

export async function updateUserPreferenceRecord(
  userId: string,
  data: UpdateUserPreference
): Promise<UserPreference> {
  const [result] = await db()
    .update(userPreference)
    .set(data)
    .where(eq(userPreference.userId, userId))
    .returning();
  return result;
}
