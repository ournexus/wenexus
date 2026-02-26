import { getTopicById } from '@/domains/discovery/services/topic-service';

import { Link } from '@/core/i18n/navigation';
import { Badge } from '@/shared/components/ui/badge';
import { Button } from '@/shared/components/ui/button';

const typeLabels: Record<string, string> = {
  debate: '辩论',
  brainstorm: '脑暴',
  analysis: '分析',
  exploration: '探索',
};

export default async function TopicDetailPage({
  params,
}: {
  params: Promise<{ id: string; locale: string }>;
}) {
  const { id } = await params;
  const topic = await getTopicById(id);

  if (!topic) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-bold">话题不存在</h1>
        <p className="text-muted-foreground mt-2">该话题可能已被删除。</p>
        <Link href="/">
          <Button variant="outline" className="mt-4">
            返回首页
          </Button>
        </Link>
      </div>
    );
  }

  const tags: string[] = Array.isArray(topic.tags) ? topic.tags : [];

  return (
    <div className="container mx-auto max-w-3xl px-4 py-8">
      <div className="space-y-6">
        <div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary">
              {typeLabels[topic.type] || topic.type}
            </Badge>
            <Badge variant="outline">
              {topic.visibility === 'public' ? '公开' : '私密'}
            </Badge>
          </div>
          <h1 className="mt-3 text-3xl font-bold">{topic.title}</h1>
          {topic.description && (
            <p className="text-muted-foreground mt-3 text-lg">
              {topic.description}
            </p>
          )}
        </div>

        {tags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => (
              <span
                key={tag}
                className="bg-muted text-muted-foreground rounded-full px-3 py-1 text-sm"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        <div className="text-muted-foreground flex items-center gap-4 text-sm">
          <span>共识度: {topic.consensusLevel ?? 0}%</span>
          <span>参与者: {topic.participantCount ?? 0}</span>
        </div>

        <Link href={`/roundtable/${topic.id}`}>
          <Button size="lg" className="w-full sm:w-auto">
            进入讨论
          </Button>
        </Link>
      </div>
    </div>
  );
}
