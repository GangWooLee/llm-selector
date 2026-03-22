from .assess_model_fit import assess_model_fit
from .compare_pricing import compare_pricing
from .get_benchmarks import get_benchmarks
from .get_model_details import get_model_details
from .search_models import search_models
from .web_search import web_search

TOOLS = [
    search_models,
    compare_pricing,
    get_benchmarks,
    assess_model_fit,
    web_search,
    get_model_details,
]
