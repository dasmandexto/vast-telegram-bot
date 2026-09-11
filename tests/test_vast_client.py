import pytest
from bot.api.vast_client import VastApiClient
from bot.api.models import SearchFilters


def test_build_url_routing():
    client = VastApiClient(api_key="test-key", base_url="https://console.vast.ai")

    # Default to /api/v0
    assert client.build_url("/instances/") == "https://console.vast.ai/api/v0/instances/"
    assert client.build_url("instances/") == "https://console.vast.ai/api/v0/instances/"
    assert client.build_url("/users/current/") == "https://console.vast.ai/api/v0/users/current/"
    
    # Explicit /api/v0
    assert client.build_url("/api/v0/bundles/") == "https://console.vast.ai/api/v0/bundles/"

    # Explicit /api/v1
    assert client.build_url("/api/v1/endpoints/") == "https://console.vast.ai/api/v1/endpoints/"

    # /v1 mapping
    assert client.build_url("/v1/serverless/") == "https://console.vast.ai/api/v1/serverless/"


def test_search_filters_model():
    filters = SearchFilters(
        gpu_name="RTX 4090",
        min_gpus=4,
        max_gpus=4,
        max_dph=2.0,
        min_reliability=0.95,
    )
    assert filters.gpu_name == "RTX 4090"
    assert filters.min_gpus == 4
    assert filters.max_gpus == 4
    assert filters.max_dph == 2.0
    assert filters.min_reliability == 0.95
