import type {
  DiscussionSession,
  DiscussionMessage,
  NewDiscussionSession,
  NewDiscussionMessage,
} from '../types';

export async function createSession(
  _input: Omit<NewDiscussionSession, 'id' | 'createdAt' | 'updatedAt'>
): Promise<DiscussionSession> {
  throw new Error('Not implemented');
}

export async function getSessionMessages(
  _sessionId: string,
  _params?: { page?: number; limit?: number }
): Promise<DiscussionMessage[]> {
  throw new Error('Not implemented');
}

export async function addMessage(
  _sessionId: string,
  _message: Omit<NewDiscussionMessage, 'id' | 'createdAt' | 'updatedAt'>
): Promise<DiscussionMessage> {
  throw new Error('Not implemented');
}
