'use client';

import React from 'react';
import {
  AgentChatProvider,
  useAgentChatContext,
} from '@/components/agent/providers/AgentChatProvider';
import { Assistant } from '@langchain/langgraph-sdk';

import { AgentChatInput } from './AgentChatInput';
import { AgentChatMessages } from './AgentChatMessages';

interface AgentChatInterfaceProps {
  assistant: Assistant | null;
  onHistoryRevalidate?: () => void;
}

function AgentChatInterfaceInner({
  assistant,
  onHistoryRevalidate,
}: AgentChatInterfaceProps) {
  const chat = useAgentChatContext();

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-hidden">
        <AgentChatMessages />
      </div>
      <div className="border-border border-t p-4">
        <AgentChatInput />
      </div>
    </div>
  );
}

export function AgentChatInterface({
  assistant,
  onHistoryRevalidate,
}: AgentChatInterfaceProps) {
  return (
    <AgentChatProvider
      activeAssistant={assistant}
      onHistoryRevalidate={onHistoryRevalidate}
    >
      <AgentChatInterfaceInner
        assistant={assistant}
        onHistoryRevalidate={onHistoryRevalidate}
      />
    </AgentChatProvider>
  );
}
