'use client';

import { useState } from 'react';

import { useRouter } from '@/core/i18n/navigation';
import { Button } from '@/shared/components/ui/button';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/shared/components/ui/card';
import { Input } from '@/shared/components/ui/input';
import { Label } from '@/shared/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/components/ui/select';

export function CreateTopicForm() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [type, setType] = useState('debate');
  const [visibility, setVisibility] = useState('public');
  const [deliverableType, setDeliverableType] = useState('report');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;

    setSubmitting(true);
    try {
      const res = await fetch('/api/domains/discovery/topics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim() || undefined,
          type,
          visibility,
          deliverableType,
        }),
      });
      const json = await res.json();
      if (json.code === 0 && json.data?.id) {
        router.push(`/roundtable/${json.data.id}`);
      }
    } catch (e) {
      console.error('Create topic failed:', e);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card className="mx-auto max-w-2xl">
      <CardHeader>
        <CardTitle>创建新话题</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="title">话题标题 *</Label>
            <Input
              id="title"
              placeholder="例如：AI 会取代程序员吗？"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">话题描述</Label>
            <textarea
              id="description"
              className="border-input bg-background ring-ring/10 flex min-h-[100px] w-full rounded-md border px-3 py-2 text-sm shadow-xs outline-none focus-visible:ring-4"
              placeholder="详细描述你想讨论的问题..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="space-y-2">
              <Label>话题类型</Label>
              <Select value={type} onValueChange={setType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="debate">辩论</SelectItem>
                  <SelectItem value="brainstorm">脑暴</SelectItem>
                  <SelectItem value="analysis">分析</SelectItem>
                  <SelectItem value="exploration">探索</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>可见性</Label>
              <Select value={visibility} onValueChange={setVisibility}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="public">公开</SelectItem>
                  <SelectItem value="private">私密</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>交付物类型</Label>
              <Select
                value={deliverableType}
                onValueChange={setDeliverableType}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="report">报告</SelectItem>
                  <SelectItem value="checklist">清单</SelectItem>
                  <SelectItem value="observation_card">观点卡片</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Button
            type="submit"
            disabled={submitting || !title.trim()}
            className="w-full"
          >
            {submitting ? '创建中...' : '开始讨论'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
