'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

import { Link } from '@/core/i18n/navigation';
import { Badge } from '@/shared/components/ui/badge';
import { Button } from '@/shared/components/ui/button';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/shared/components/ui/card';

interface TopicInfo {
  id: string;
  title: string;
  description: string | null;
  type: string;
  consensusLevel: number;
}

interface Message {
  id: string;
  role: string;
  content: string;
  expertId: string | null;
  citations: any;
  metadata: any;
  createdAt: string;
}

interface ConsensusState {
  level: number;
  agreements: string[];
  disagreements: string[];
  undecided: string[];
}

const roleLabels: Record<string, string> = {
  fact_checker: '求真者',
  expert: '专家',
  host: '主持人',
  participant: '参与者',
  system: '系统',
};

const roleBadgeVariants: Record<string, 'default' | 'secondary' | 'outline'> = {
  fact_checker: 'secondary',
  expert: 'default',
  host: 'outline',
};

export function RoundtableClient({
  topic,
  sessionId: initialSessionId,
  initialStatus,
}: {
  topic: TopicInfo;
  sessionId: string;
  initialStatus: string;
}) {
  const sessionId = initialSessionId;
  const [messages, setMessages] = useState<Message[]>([]);
  const [consensus, setConsensus] = useState<ConsensusState | null>(null);
  const [loading, setLoading] = useState(false);
  const [phase, setPhase] = useState<string>(initialStatus);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Load messages for session
  const loadMessages = useCallback(async () => {
    try {
      const res = await fetch(
        `/api/domains/roundtable/messages?sessionId=${sessionId}`
      );
      const json = await res.json();
      if (json.code === 0) {
        setMessages(json.data.messages);
        // Update phase based on existing messages
        if (json.data.messages.length > 0) {
          const hasFactCheck = json.data.messages.some(
            (m: Message) => m.role === 'fact_checker'
          );
          if (hasFactCheck) setPhase('discussing');
        }
      }
    } catch (e: any) {
      console.error('Failed to load messages:', e);
    }
  }, [sessionId]);

  // Initialize on mount
  useEffect(() => {
    loadMessages();
  }, [loadMessages]);

  // Start discussion (fact checker)
  const handleStartDiscussion = async () => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    setPhase('fact_checking');
    try {
      const res = await fetch(
        `/api/domains/roundtable/sessions/${sessionId}/start`,
        { method: 'POST' }
      );
      const json = await res.json();
      if (json.code === 0) {
        setMessages((prev) => [...prev, json.data]);
        setPhase('discussing');
      } else {
        setError(json.message);
        setPhase('initializing');
      }
    } catch (e: any) {
      setError(e.message);
      setPhase('initializing');
    } finally {
      setLoading(false);
    }
  };

  // Next expert turn
  const handleNextTurn = async () => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `/api/domains/roundtable/sessions/${sessionId}/next-turn`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({}),
        }
      );
      const json = await res.json();
      if (json.code === 0) {
        setMessages((prev) => [...prev, json.data]);
      } else {
        setError(json.message);
      }
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  // Get consensus
  const handleGetConsensus = async () => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `/api/domains/roundtable/sessions/${sessionId}/consensus`,
        { method: 'POST' }
      );
      const json = await res.json();
      if (json.code === 0) {
        setConsensus(json.data);
      } else {
        setError(json.message);
      }
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const expertMessages = messages.filter((m) => m.role === 'expert');
  const canStart =
    phase === 'initializing' && messages.length === 0 && !loading;
  const canNextTurn = phase === 'discussing' && !loading;
  const canGetConsensus = expertMessages.length >= 2 && !loading;

  return (
    <div className="container mx-auto max-w-4xl px-4 py-6">
      {/* Header */}
      <div className="mb-6">
        <Link
          href={`/topic/${topic.id}`}
          className="text-muted-foreground hover:text-foreground mb-2 inline-block text-sm"
        >
          ← 返回话题
        </Link>
        <h1 className="text-2xl font-bold">{topic.title}</h1>
        {topic.description && (
          <p className="text-muted-foreground mt-1">{topic.description}</p>
        )}
        <div className="mt-2 flex items-center gap-2">
          <Badge variant="secondary">{topic.type}</Badge>
          <Badge variant="outline">共识度 {topic.consensusLevel}%</Badge>
          {sessionId && (
            <span className="text-muted-foreground text-xs">
              会话: {sessionId.slice(0, 8)}...
            </span>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300">
          {error}
        </div>
      )}

      {/* Messages */}
      <div className="mb-6 space-y-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {loading && (
          <div className="flex items-center gap-2 py-4">
            <div className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:-0.3s]" />
            <div className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:-0.15s]" />
            <div className="h-2 w-2 animate-bounce rounded-full bg-current" />
            <span className="text-muted-foreground ml-2 text-sm">
              {phase === 'fact_checking'
                ? '求真者正在核查事实...'
                : '专家正在思考...'}
            </span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Controls */}
      <div className="bg-background sticky bottom-0 border-t pt-4 pb-6">
        <div className="flex flex-wrap gap-3">
          {canStart && (
            <Button onClick={handleStartDiscussion} size="lg">
              开始讨论
            </Button>
          )}
          {canNextTurn && (
            <Button onClick={handleNextTurn} size="lg">
              下一轮发言
            </Button>
          )}
          {canGetConsensus && (
            <Button onClick={handleGetConsensus} variant="outline" size="lg">
              查看共识度
            </Button>
          )}
        </div>

        {/* Consensus panel */}
        {consensus && (
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                共识度分析
                <Badge variant="default">{consensus.level}%</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {consensus.agreements.length > 0 && (
                <div>
                  <h4 className="mb-1 text-sm font-medium text-green-600 dark:text-green-400">
                    共识点
                  </h4>
                  <ul className="list-inside list-disc space-y-1 text-sm">
                    {consensus.agreements.map((a, i) => (
                      <li key={i}>{a}</li>
                    ))}
                  </ul>
                </div>
              )}
              {consensus.disagreements.length > 0 && (
                <div>
                  <h4 className="mb-1 text-sm font-medium text-red-600 dark:text-red-400">
                    分歧点
                  </h4>
                  <ul className="list-inside list-disc space-y-1 text-sm">
                    {consensus.disagreements.map((d, i) => (
                      <li key={i}>{d}</li>
                    ))}
                  </ul>
                </div>
              )}
              {consensus.undecided.length > 0 && (
                <div>
                  <h4 className="text-muted-foreground mb-1 text-sm font-medium">
                    待定
                  </h4>
                  <ul className="list-inside list-disc space-y-1 text-sm">
                    {consensus.undecided.map((u, i) => (
                      <li key={i}>{u}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isFactChecker = message.role === 'fact_checker';

  return (
    <Card
      className={isFactChecker ? 'border-blue-200 dark:border-blue-800' : ''}
    >
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <Badge variant={roleBadgeVariants[message.role] || 'outline'}>
            {roleLabels[message.role] || message.role}
          </Badge>
          <span className="text-muted-foreground text-xs">
            {new Date(message.createdAt).toLocaleTimeString()}
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap">
          {message.content}
        </div>
        {message.citations &&
          Array.isArray(message.citations) &&
          message.citations.length > 0 && (
            <div className="mt-3 border-t pt-2">
              <h5 className="text-muted-foreground mb-1 text-xs font-medium">
                参考来源
              </h5>
              <ul className="space-y-1">
                {(message.citations as any[]).map((c: any, i: number) => {
                  const isSafeUrl =
                    typeof c.url === 'string' && /^https?:\/\//i.test(c.url);
                  return (
                    <li key={i} className="text-xs">
                      {isSafeUrl ? (
                        <a
                          href={c.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline dark:text-blue-400"
                        >
                          {c.title}
                        </a>
                      ) : (
                        <span className="text-blue-600 dark:text-blue-400">
                          {c.title}
                        </span>
                      )}
                      {c.snippet && (
                        <span className="text-muted-foreground">
                          {' '}
                          — {c.snippet}
                        </span>
                      )}
                    </li>
                  );
                })}
              </ul>
            </div>
          )}
      </CardContent>
    </Card>
  );
}
