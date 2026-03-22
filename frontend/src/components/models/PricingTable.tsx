import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface PricingTableProps {
  pricingInput: number;
  pricingOutput: number;
  isFree: boolean;
}

function formatPrice(price: number): string {
  if (price === 0) return "Free";
  if (price < 0.01) return `$${price.toFixed(6)}`;
  return `$${price.toFixed(2)}`;
}

export function PricingTable({
  pricingInput,
  pricingOutput,
  isFree,
}: PricingTableProps) {
  return (
    <div>
      <h2 className="text-base font-semibold mb-3">Pricing</h2>
      {isFree ? (
        <p className="text-sm text-emerald-600 dark:text-emerald-400 font-medium">
          This model is free to use.
        </p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Type</TableHead>
              <TableHead>Per 1M Tokens</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell>Input</TableCell>
              <TableCell className="font-mono">
                {formatPrice(pricingInput)}
              </TableCell>
            </TableRow>
            <TableRow>
              <TableCell>Output</TableCell>
              <TableCell className="font-mono">
                {formatPrice(pricingOutput)}
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      )}
    </div>
  );
}
