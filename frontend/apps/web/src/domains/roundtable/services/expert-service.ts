import type { Expert, NewExpert } from '../types';

export async function getBuiltinExperts(): Promise<Expert[]> {
  throw new Error('Not implemented');
}

export async function createCustomExpert(
  _userId: string,
  _input: Omit<NewExpert, 'id' | 'createdAt' | 'updatedAt'>
): Promise<Expert> {
  throw new Error('Not implemented');
}

export async function getExpertsForSession(
  _sessionId: string
): Promise<Expert[]> {
  throw new Error('Not implemented');
}
