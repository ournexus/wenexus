'use client';

import { useEffect, useRef, useState } from 'react';
import { Loader2, Send } from 'lucide-react';

import { Button } from '@/shared/components/ui/button';

interface MessageInputProps {
  sessionId: string;
  onMessageSent?: (message: {
    userMessage: any;
    aiReplies: any[];
    status: string;
  }) => void;
  disabled?: boolean;
}

export function MessageInput({
  sessionId,
  onMessageSent,
  disabled = false,
}: MessageInputProps) {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = inputRef.current;
    if (!textarea) return;

    const adjustHeight = () => {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    };

    textarea.addEventListener('input', adjustHeight);
    return () => textarea.removeEventListener('input', adjustHeight);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!content.trim()) {
      setError('Please enter a message');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/domains/roundtable/messages/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sessionId,
          content: content.trim(),
          generateAiReply: true,
        }),
      });

      const data = await response.json();

      if (data.code === 0) {
        setContent('');
        if (inputRef.current) {
          inputRef.current.style.height = 'auto';
        }
        onMessageSent?.(data.data);
      } else {
        setError(data.message || 'Failed to send message');
      }
    } catch (err: any) {
      console.error('Error sending message:', err);
      setError(err.message || 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Ctrl+Enter or Cmd+Enter
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-background border-t p-4">
      <div className="flex flex-col gap-2">
        {error && (
          <div className="bg-destructive/10 text-destructive rounded-md px-3 py-2 text-sm">
            {error}
          </div>
        )}

        <div className="flex gap-2">
          <textarea
            ref={inputRef}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入消息... (Ctrl+Enter 发送)"
            disabled={loading || disabled}
            className="border-input bg-background placeholder:text-muted-foreground min-h-12 flex-1 resize-none rounded-md border px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50"
            rows={1}
          />
          <Button
            type="submit"
            disabled={loading || disabled || !content.trim()}
            className="h-12 self-end"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
            <span className="ml-2 hidden sm:inline">发送</span>
          </Button>
        </div>

        <div className="text-muted-foreground text-xs">
          按 Ctrl+Enter 或 Cmd+Enter 快速发送
        </div>
      </div>
    </form>
  );
}
