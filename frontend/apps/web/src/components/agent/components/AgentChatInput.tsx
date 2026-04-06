'use client';

import { useState } from 'react';
import { useAgentChatContext } from '@/components/agent/providers/AgentChatProvider';
import { Send } from 'lucide-react';

import { Button } from '@/shared/components/ui/button';
import { Textarea } from '@/shared/components/ui/textarea';

export function AgentChatInput() {
  const [input, setInput] = useState('');
  const { sendMessage, isLoading } = useAgentChatContext();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      sendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your message..."
        className="max-h-[120px] min-h-[40px] flex-1 resize-none"
        disabled={isLoading}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
          }
        }}
      />
      <Button type="submit" size="icon" disabled={!input.trim() || isLoading}>
        <Send className="h-4 w-4" />
      </Button>
    </form>
  );
}
