import type {
  UpdateUserPreference,
  UserIdentity,
  UserPreference,
} from '../types';

export async function getUserPreference(
  _userId: string
): Promise<UserPreference | null> {
  throw new Error('Not implemented');
}

export async function updateUserPreference(
  _userId: string,
  _update: UpdateUserPreference
): Promise<UserPreference> {
  throw new Error('Not implemented');
}

export async function getUserIdentity(_userId: string): Promise<UserIdentity> {
  throw new Error('Not implemented');
}
