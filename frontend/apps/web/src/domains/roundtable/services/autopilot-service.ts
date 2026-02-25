import type { AutopilotState, SessionMode } from '../types';

export async function getAutopilotState(
  _sessionId: string
): Promise<AutopilotState> {
  throw new Error('Not implemented');
}

export async function switchMode(
  _sessionId: string,
  _mode: SessionMode
): Promise<void> {
  throw new Error('Not implemented');
}
