export default async function TopicDetailPage({
  params,
}: {
  params: Promise<{ id: string; locale: string }>;
}) {
  const { id } = await params;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold">Topic Detail</h1>
      <p className="mt-2 text-muted-foreground">Topic ID: {id}</p>
      <p className="mt-4 text-sm text-muted-foreground">
        This page will display topic details and observation cards.
      </p>
    </div>
  );
}
