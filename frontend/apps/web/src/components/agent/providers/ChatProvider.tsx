'use client';

import { createContext, ReactNode, useContext } from 'react';
import { useChat, type StateType } from '@/app/hooks/useChat';
import { Assistant } from '@langchain/langgraph-sdk';
import type { UseStreamThread } from '@langchain/langgraph-sdk/react';

interface ChatProviderProps {
  children: ReactNode;
  activeAssistant: Assistant | null;
  onHistoryRevalidate?: () => void;
  thread?: UseStreamThread<StateType>;
}

export function ChatProvider({
  children,
  activeAssistant,
  onHistoryRevalidate,
  thread,
}: ChatProviderProps) {
  const chat = useChat({ activeAssistant, onHistoryRevalidate, thread });
  return <ChatContext.Provider value={chat}>{children}</ChatContext.Provider>;
}

export type ChatContextType = ReturnType<typeof useChat>;

export const ChatContext = createContext<ChatContextType | undefined>(
  undefined
);

export function useChatContext() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
}
