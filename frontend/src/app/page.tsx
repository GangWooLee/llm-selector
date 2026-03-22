import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <section className="mb-12 text-center">
        <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
          Find the Right LLM for Your Use Case
        </h2>
        <p className="mt-4 text-lg text-muted-foreground">
          Describe what you need, and our AI advisor will analyze real-time data
          to recommend the best models with evidence-based comparisons.
        </p>
      </section>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Usage Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Describe your use case in natural language. Our agent analyzes
              your requirements including performance, budget, and capabilities.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Model Matching</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Search across hundreds of models with real-time pricing and
              benchmark data from our continuously synced database.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Evidence-Based Report</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Get a detailed comparison report with scores, cost simulations,
              and transparent reasoning for every recommendation.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
