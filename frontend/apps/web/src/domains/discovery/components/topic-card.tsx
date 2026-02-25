'use client';

import { Link } from '@/core/i18n/navigation';
import { Badge } from '@/shared/components/ui/badge';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/shared/components/ui/card';

interface TopicCardProps {
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
  expertCount?: number;
}

const typeLabels: Record<string, string> = {
  debate: '辩论',
  brainstorm: '脑暴',
  analysis: '分析',
  exploration: '探索',
};

export function TopicCard({ topic, expertCount = 4 }: TopicCardProps) {
  const tags: string[] = topic.tags ? JSON.parse(topic.tags) : [];

  return (
    <Link href={`/topic/${topic.id}`}>
      <Card className="group cursor-pointer transition-shadow hover:shadow-md">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Badge variant="secondary">
              {typeLabels[topic.type] || topic.type}
            </Badge>
            {topic.status === 'discussing' && (
              <Badge variant="default">讨论中</Badge>
            )}
          </div>
          <CardTitle className="group-hover:text-primary line-clamp-2 text-lg">
            {topic.title}
          </CardTitle>
          {topic.description && (
            <CardDescription className="line-clamp-2">
              {topic.description}
            </CardDescription>
          )}
        </CardHeader>
        <CardContent>
          {tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {tags.slice(0, 4).map((tag) => (
                <span
                  key={tag}
                  className="bg-muted text-muted-foreground rounded-full px-2 py-0.5 text-xs"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </CardContent>
        <CardFooter className="text-muted-foreground text-xs">
          <div className="flex w-full items-center justify-between">
            <span>{expertCount} 位专家</span>
            <span>共识度 {topic.consensusLevel ?? 0}%</span>
          </div>
        </CardFooter>
      </Card>
    </Link>
  );
}
