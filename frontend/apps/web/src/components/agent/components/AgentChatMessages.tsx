'use client';

import { useAgentChatContext } from '@/components/agent/providers/AgentChatProvider';

function extractTextContent(content: unknown): string {
  if (typeof content === 'string') return content;
  if (Array.isArray(content)) {
    return content
      .map((block: unknown) => {
        if (typeof block === 'string') return block;
        if (block && typeof block === 'object' && 'text' in block) {
          return String((block as { text: unknown }).text);
        }
        return '';
      })
      .filter(Boolean)
      .join('\n');
  }
  return '';
}

function ToolCallIndicator({ toolCalls }: { toolCalls: { name: string }[] }) {
  return (
    <div className="flex justify-start">
      <div className="bg-muted/60 border-border text-muted-foreground max-w-[80%] rounded-lg border px-4 py-2">
        <p className="mb-1 text-xs font-medium tracking-wide uppercase">
          Using tools
        </p>
        <div className="flex flex-wrap gap-1">
          {toolCalls.map((tc, i) => (
            <span
              key={i}
              className="bg-background border-border rounded border px-2 py-0.5 font-mono text-xs"
            >
              {tc.name}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

export function AgentChatMessages() {
  const { messages, isLoading } = useAgentChatContext();

  return (
    <div className="flex-1 space-y-4 overflow-y-auto p-4">
      {messages.length === 0 ? (
        <div className="text-muted-foreground py-8 text-center">
          <p>No messages yet. Start a conversation!</p>
        </div>
      ) : (
        messages.map((message: any, index: number) => {
          const text = extractTextContent(message.content);
          const toolCalls: { name: string }[] = message.tool_calls ?? [];
          const isHuman = message.type === 'human';

          const isAi =
            message.type === 'ai' || message.type === 'AIMessageChunk';
          const isTool =
            message.type === 'tool' || message.type === 'ToolMessage';

          // Tool result messages — hide them (internal, already reflected in AI reply)
          if (isTool) return null;

          // AI message with tool calls but no readable content → show indicator
          if (isAi && !text && toolCalls.length > 0) {
            return (
              <ToolCallIndicator
                key={message.id ?? index}
                toolCalls={toolCalls}
              />
            );
          }

          // Skip truly empty messages
          if (!text) return null;

          return (
            <div
              key={message.id ?? index}
              className={`flex ${isHuman ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  isHuman ? 'bg-primary text-primary-foreground' : 'bg-muted'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{text}</p>
              </div>
            </div>
          );
        })
      )}

      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-muted rounded-lg px-4 py-2">
            <p className="text-muted-foreground text-sm">Thinking…</p>
          </div>
        </div>
      )}
    </div>
  );
}
