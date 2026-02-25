import { getUuid } from '@/shared/lib/hash';

import { findSessionById } from '../models/discussion-session';
import {
  createExpertRecord,
  findExpertById,
  getExperts,
} from '../models/expert';
import type { Expert, NewExpert } from '../types';

export async function getBuiltinExperts(): Promise<Expert[]> {
  return getExperts({ isBuiltin: true, status: 'active' });
}

export async function createCustomExpert(
  userId: string,
  input: Omit<NewExpert, 'id' | 'createdAt' | 'updatedAt'>
): Promise<Expert> {
  const id = getUuid();
  return createExpertRecord({
    id,
    ...input,
    createdByUserId: userId,
    isBuiltin: false,
  });
}

export async function getExpertsForSession(
  sessionId: string
): Promise<Expert[]> {
  const session = await findSessionById(sessionId);
  if (!session) return [];

  const expertIds: string[] = session.expertIds
    ? JSON.parse(session.expertIds)
    : [];

  if (expertIds.length === 0) {
    return getBuiltinExperts();
  }

  const experts = await Promise.all(expertIds.map((id) => findExpertById(id)));
  return experts.filter((e): e is Expert => e !== undefined);
}
