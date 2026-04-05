'use client';

import { useCallback } from 'react';
import { MessageSquare, X } from 'lucide-react';

import { Button } from '@/shared/components/ui/button';
import { Card } from '@/shared/components/ui/card';

interface AgentThreadListProps {
  assistantId: string;
  onThreadSelect: (id: string) => Promise<void>;
  onMutateReady: (fn: () => void) => void;
  onClose: () => void;
  onInterruptCountChange: (count: number) => void;
}

export function AgentThreadList({
  assistantId,
  onThreadSelect,
  onMutateReady,
  onClose,
  onInterruptCountChange,
}: AgentThreadListProps) {
  // TODO: Implement actual thread fetching
  const threads = [];

  const handleThreadSelect = async (threadId: string) => {
    await onThreadSelect(threadId);
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b p-4">
        <h2 className="text-lg font-semibold">Threads</h2>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {threads.length === 0 ? (
          <div className="text-muted-foreground py-8 text-center">
            <MessageSquare className="mx-auto mb-4 h-12 w-12 opacity-50" />
            <p>No threads yet</p>
            <p className="text-sm">Start a new conversation to see it here</p>
          </div>
        ) : (
          <div className="space-y-2">
            {threads.map((thread: any) => (
              <Card
                key={thread.id}
                className="hover:bg-accent cursor-pointer p-3 transition-colors"
                onClick={() => handleThreadSelect(thread.id)}
              >
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-4 w-4" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">
                      {thread.title}
                    </p>
                    <p className="text-muted-foreground truncate text-xs">
                      {thread.description}
                    </p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
