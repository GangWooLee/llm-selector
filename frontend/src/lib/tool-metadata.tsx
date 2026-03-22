import {
  Search,
  DollarSign,
  BarChart3,
  Globe,
  CheckCircle,
  Info,
} from "lucide-react";

export const TOOL_ICON_COMPONENTS: Record<string, React.ReactNode> = {
  search_models: <Search className="size-4 text-muted-foreground" />,
  compare_pricing: <DollarSign className="size-4 text-muted-foreground" />,
  get_benchmarks: <BarChart3 className="size-4 text-muted-foreground" />,
  web_search: <Globe className="size-4 text-muted-foreground" />,
  assess_model_fit: <CheckCircle className="size-4 text-muted-foreground" />,
  get_model_details: <Info className="size-4 text-muted-foreground" />,
};

export const TOOL_DISPLAY_LABELS: Record<string, string> = {
  search_models: "Model Search",
  compare_pricing: "Price Comparison",
  get_benchmarks: "Benchmarks",
  web_search: "Web Search",
  assess_model_fit: "Fit Assessment",
  get_model_details: "Model Details",
};
