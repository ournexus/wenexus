export default async function RoundtablePage({
  params,
}: {
  params: Promise<{ topicId: string; locale: string }>;
}) {
  const { topicId } = await params;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold">Roundtable Discussion</h1>
      <p className="mt-2 text-muted-foreground">Topic ID: {topicId}</p>
      <p className="mt-4 text-sm text-muted-foreground">
        This page will host the AI expert roundtable discussion interface.
      </p>
    </div>
  );
}
