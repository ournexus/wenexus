'use client';

import { createContext, ReactNode, useContext, useMemo } from 'react';
import { Client } from '@langchain/langgraph-sdk';

interface AgentClientContextValue {
  client: Client;
}

const AgentClientContext = createContext<AgentClientContextValue | null>(null);

interface AgentClientProviderProps {
  children: ReactNode;
  deploymentUrl: string;
  apiKey: string;
}

export function AgentClientProvider({
  children,
  deploymentUrl,
  apiKey,
}: AgentClientProviderProps) {
  const client = useMemo(() => {
    return new Client({
      apiUrl: deploymentUrl,
      defaultHeaders: {
        'Content-Type': 'application/json',
        'X-Api-Key': apiKey,
      },
    });
  }, [deploymentUrl, apiKey]);

  const value = useMemo(() => ({ client }), [client]);

  return (
    <AgentClientContext.Provider value={value}>
      {children}
    </AgentClientContext.Provider>
  );
}

export function useAgentClient(): Client {
  const context = useContext(AgentClientContext);

  if (!context) {
    throw new Error(
      'useAgentClient must be used within an AgentClientProvider'
    );
  }
  return context.client;
}
