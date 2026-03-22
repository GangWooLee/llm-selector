import { Progress } from "@/components/ui/progress";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Benchmark } from "@/types/model";

interface BenchmarkTableProps {
  benchmarks: Benchmark[];
}

export function BenchmarkTable({ benchmarks }: BenchmarkTableProps) {
  if (benchmarks.length === 0) {
    return (
      <div>
        <h2 className="text-base font-semibold mb-3">Benchmarks</h2>
        <p className="text-sm text-muted-foreground">
          No benchmark data available for this model.
        </p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-base font-semibold mb-3">Benchmarks</h2>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Benchmark</TableHead>
            <TableHead>Score</TableHead>
            <TableHead className="w-32">Progress</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {benchmarks.map((benchmark) => {
            const percentage =
              benchmark.max_score > 0
                ? (benchmark.score / benchmark.max_score) * 100
                : 0;

            return (
              <TableRow key={benchmark.benchmark_name}>
                <TableCell>
                  {benchmark.source_url ? (
                    <a
                      href={benchmark.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="underline underline-offset-4 hover:text-primary"
                      aria-label={`${benchmark.benchmark_name} (opens in new window)`}
                    >
                      {benchmark.benchmark_name}
                    </a>
                  ) : (
                    benchmark.benchmark_name
                  )}
                </TableCell>
                <TableCell className="font-mono">
                  {benchmark.score} / {benchmark.max_score}
                </TableCell>
                <TableCell>
                  <Progress value={percentage} className="h-2" />
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
