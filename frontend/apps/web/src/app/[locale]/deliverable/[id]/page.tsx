export default async function DeliverablePage({
  params,
}: {
  params: Promise<{ id: string; locale: string }>;
}) {
  const { id } = await params;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold">Deliverable</h1>
      <p className="mt-2 text-muted-foreground">Deliverable ID: {id}</p>
      <p className="mt-4 text-sm text-muted-foreground">
        This page will display generated deliverables (reports, articles, scripts, etc.).
      </p>
    </div>
  );
}
