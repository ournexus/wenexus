import { FeedView } from '@/domains/discovery/components';

import { Link } from '@/core/i18n/navigation';
import { Button } from '@/shared/components/ui/button';

export default function DiscoverPage() {
  return (
    <div className="container mx-auto max-w-6xl px-4 py-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">发现</h1>
          <p className="text-muted-foreground mt-1">
            探索多元视角，理解复杂世界
          </p>
        </div>
        <Link href="/topic/create">
          <Button>创建话题</Button>
        </Link>
      </div>
      <FeedView />
    </div>
  );
}
