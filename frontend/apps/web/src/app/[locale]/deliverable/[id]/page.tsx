export default async function DeliverablePage({
  params,
}: {
  params: Promise<{ id: string; locale: string }>;
}) {
  const { id } = await params;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold">Deliverable</h1>
      <p className="text-muted-foreground mt-2">Deliverable ID: {id}</p>
      <p className="text-muted-foreground mt-4 text-sm">
        This page will display generated deliverables (reports, articles,
        scripts, etc.).
      </p>
    </div>
  );
}
