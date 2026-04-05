'use client';

import { createContext, ReactNode, useContext } from 'react';
import {
  useAgentChat,
  type AgentStateType,
} from '@/components/agent/hooks/useAgentChat';
import { Assistant } from '@langchain/langgraph-sdk';
import type { UseStreamThread } from '@langchain/langgraph-sdk/react';

interface AgentChatProviderProps {
  children: ReactNode;
  activeAssistant: Assistant | null;
  onHistoryRevalidate?: () => void;
  thread?: UseStreamThread<AgentStateType>;
}

export function AgentChatProvider({
  children,
  activeAssistant,
  onHistoryRevalidate,
  thread,
}: AgentChatProviderProps) {
  const chat = useAgentChat({ activeAssistant, onHistoryRevalidate, thread });
  return (
    <AgentChatContext.Provider value={chat}>
      {children}
    </AgentChatContext.Provider>
  );
}

export type AgentChatContextType = ReturnType<typeof useAgentChat>;

export const AgentChatContext = createContext<AgentChatContextType | undefined>(
  undefined
);

export function useAgentChatContext() {
  const context = useContext(AgentChatContext);
  if (context === undefined) {
    throw new Error(
      'useAgentChatContext must be used within an AgentChatProvider'
    );
  }
  return context;
}
