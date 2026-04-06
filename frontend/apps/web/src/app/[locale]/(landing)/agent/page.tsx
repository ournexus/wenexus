'use client';

import React, { Suspense, useCallback, useEffect, useState } from 'react';
import { AgentChatInterface } from '@/components/agent/components/AgentChatInterface';
import { AgentThreadList } from '@/components/agent/components/AgentThreadList';
import {
  AgentClientProvider,
  useAgentClient,
} from '@/components/agent/providers/AgentClientProvider';
import { Assistant } from '@langchain/langgraph-sdk';
import { MessagesSquare, SquarePen } from 'lucide-react';

import { Button } from '@/shared/components/ui/button';

interface AgentPageInnerProps {
  assistantId: string;
  deploymentUrl: string;
  apiKey: string;
}

function AgentPageInner({
  assistantId,
  deploymentUrl,
  apiKey,
}: AgentPageInnerProps) {
  const client = useAgentClient();
  const [threadId, setThreadId] = useState<string | null>(null);
  const [sidebar, setSidebar] = useState<string | null>(null);

  const [mutateThreads, setMutateThreads] = useState<(() => void) | null>(null);
  const [interruptCount, setInterruptCount] = useState(0);
  const [assistant, setAssistant] = useState<Assistant | null>(null);

  const fetchAssistant = useCallback(async () => {
    const isUUID =
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
        assistantId
      );

    if (isUUID) {
      // We should try to fetch the assistant directly with this UUID
      try {
        const data = await client.assistants.get(assistantId);
        setAssistant(data);
      } catch (error) {
        console.error('Failed to fetch assistant:', error);
        setAssistant({
          assistant_id: assistantId,
          graph_id: assistantId,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          config: {},
          metadata: {},
          version: 1,
          name: 'Assistant',
          context: {},
        });
      }
    } else {
      try {
        // We should try to list out the assistants for this graph, and then use the default one.
        const assistants = await client.assistants.search({
          graphId: assistantId,
          limit: 100,
        });
        const defaultAssistant = assistants.find(
          (assistant) => assistant.metadata?.['created_by'] === 'system'
        );
        if (defaultAssistant === undefined) {
          throw new Error('No default assistant found');
        }
        setAssistant(defaultAssistant);
      } catch (error) {
        console.error(
          'Failed to find default assistant from graph_id: try setting the assistant_id directly:',
          error
        );
        setAssistant({
          assistant_id: assistantId,
          graph_id: assistantId,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          config: {},
          metadata: {},
          version: 1,
          name: assistantId,
          context: {},
        });
      }
    }
  }, [client, assistantId]);

  useEffect(() => {
    fetchAssistant();
  }, [fetchAssistant]);

  return (
    <div className="flex h-screen flex-col">
      <header className="border-border flex h-16 items-center justify-between border-b px-6">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-semibold">Agent Chat</h1>
          {!sidebar && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebar('1')}
              className="border-border bg-card text-foreground hover:bg-accent rounded-md border p-3"
            >
              <MessagesSquare className="mr-2 h-4 w-4" />
              Threads
              {interruptCount > 0 && (
                <span className="bg-destructive text-destructive-foreground ml-2 inline-flex min-h-4 min-w-4 items-center justify-center rounded-full px-1 text-[10px]">
                  {interruptCount}
                </span>
              )}
            </Button>
          )}
        </div>
        <div className="flex items-center gap-2">
          <div className="text-muted-foreground text-sm">
            <span className="font-medium">Assistant:</span> {assistantId}
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setThreadId(null)}
            disabled={!threadId}
            className="border-[#2F6868] bg-[#2F6868] text-white hover:bg-[#2F6868]/80"
          >
            <SquarePen className="mr-2 h-4 w-4" />
            New Thread
          </Button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {sidebar && (
          <div className="border-border w-80 shrink-0 overflow-hidden border-r">
            <AgentThreadList
              assistantId={assistantId}
              onThreadSelect={async (id: string) => {
                await setThreadId(id);
              }}
              onMutateReady={(fn: () => void) => setMutateThreads(() => fn)}
              onClose={() => setSidebar(null)}
              onInterruptCountChange={setInterruptCount}
            />
          </div>
        )}
        <div className="relative flex flex-1 flex-col overflow-hidden">
          <AgentChatInterface
            assistant={assistant}
            onHistoryRevalidate={() => mutateThreads?.()}
          />
        </div>
      </div>
    </div>
  );
}

function AgentPageContent() {
  const [assistantId] = useState<string | null>(
    typeof window !== 'undefined'
      ? new URLSearchParams(window.location.search).get('assistantId')
      : null
  );

  // Default to researchAgent assistant if none specified
  const defaultAssistantId = assistantId || 'researchAgent';

  // Configuration for LangGraph API
  const deploymentUrl = 'http://localhost:8000/langgraph';
  const apiKey = ''; // TODO: Get from environment or config

  return (
    <AgentClientProvider deploymentUrl={deploymentUrl} apiKey={apiKey}>
      <AgentPageInner
        assistantId={defaultAssistantId}
        deploymentUrl={deploymentUrl}
        apiKey={apiKey}
      />
    </AgentClientProvider>
  );
}

export default function AgentPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-screen items-center justify-center">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      }
    >
      <AgentPageContent />
    </Suspense>
  );
}
