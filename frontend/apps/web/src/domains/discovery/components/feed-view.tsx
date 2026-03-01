'use client';

import { useEffect, useState } from 'react';

import { TopicCard } from './topic-card';

interface FeedCardData {
  topic: {
    id: string;
    title: string;
    description: string | null;
    type: string;
    status: string;
    consensusLevel: number | null;
    participantCount: number | null;
    tags: string | null;
    createdAt: Date;
  };
  expertCount: number;
  consensusLevel: number;
}

export function FeedView() {
  const [cards, setCards] = useState<FeedCardData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadFeed() {
      try {
        const res = await fetch('/api/domains/discovery/feed');
        const json = await res.json();
        if (json.code === 0) {
          setCards(json.data.cards);
        }
      } catch (e) {
        console.error('Failed to load feed:', e);
      } finally {
        setLoading(false);
      }
    }
    loadFeed();
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-muted h-48 animate-pulse rounded-xl" />
        ))}
      </div>
    );
  }

  if (cards.length === 0) {
    return (
      <div className="text-muted-foreground py-12 text-center">
        <p>还没有话题，创建第一个吧。</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      {cards.map((card) => (
        <TopicCard
          key={card.topic.id}
          topic={card.topic}
          expertCount={card.expertCount}
        />
      ))}
    </div>
  );
}
