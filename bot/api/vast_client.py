import json
import logging
import re
from typing import Any, Dict, List, Optional
import httpx

from .models import Offer, Instance, UserInfo, SearchFilters

logger = logging.getLogger(__name__)


class VastApiError(Exception):
    """Base exception for Vast.ai API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class VastApiClient:
    def __init__(self, api_key: str, base_url: str = "https://console.vast.ai", timeout: float = 30.0):
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.fallback_url = "https://cloud.vast.ai" if "console" in self.base_url else "https://console.vast.ai"
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json",
                    "User-Agent": "VastAITelegramBot/1.0",
                },
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def build_url(self, endpoint: str, base: Optional[str] = None) -> str:
        """
        Builds full URL following Vast.ai API guidelines:
        - If endpoint starts with /api/v0 or /api/v1, use directly with base
        - If endpoint starts with /v0 or /v1, map to /api/vX
        - Otherwise, default to /api/v0/<endpoint>
        """
        base = (base or self.base_url).rstrip("/")
        endpoint = endpoint.strip()
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint

        if re.match(r"^/api/v\d+/", endpoint):
            path = endpoint
        elif re.match(r"^/v\d+/", endpoint):
            path = "/api" + endpoint
        else:
            path = "/api/v0" + endpoint

        return f"{base}{path}"

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        client = await self.get_client()
        url = self.build_url(endpoint)

        try:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Fallback to alternate domain if server error or DNS/connectivity issue
            logger.warning("Request failed on %s (%s). Attempting fallback...", url, e.response.status_code)
            fallback_url = self.build_url(endpoint, base=self.fallback_url)
            try:
                fb_resp = await client.request(
                    method=method,
                    url=fallback_url,
                    params=params,
                    json=json_data,
                )
                fb_resp.raise_for_status()
                return fb_resp.json()
            except Exception:
                # Raise original error with details
                error_text = e.response.text
                try:
                    err_json = e.response.json()
                    error_text = err_json.get("msg") or err_json.get("error") or str(err_json)
                except Exception:
                    pass
                raise VastApiError(
                    f"Vast.ai API error ({e.response.status_code}): {error_text}",
                    status_code=e.response.status_code,
                    response_body=e.response.text,
                ) from e
        except httpx.RequestError as e:
            logger.error("Connection error to Vast.ai API: %s", str(e))
            raise VastApiError(f"Network error connecting to Vast.ai: {str(e)}") from e

    async def get_user_info(self) -> UserInfo:
        """Get current user account balance, credits and spend."""
        data = await self._request("GET", "/users/current/")
        return UserInfo(
            user_id=data.get("id"),
            email=data.get("email"),
            balance=float(data.get("balance") or 0.0),
            credit=float(data.get("credit") or 0.0),
            total_spend=float(data.get("billed_cost") or data.get("total_spend") or 0.0),
            billed_cost=float(data.get("billed_cost") or 0.0),
        )

    async def get_instances(self) -> List[Instance]:
        """Get all user instances (running, stopped, loading)."""
        data = await self._request("GET", "/api/v1/instances/", params={"owner": "me"})
        instances_raw = data.get("instances", []) if isinstance(data, dict) else data
        result = []
        for item in instances_raw:
            try:
                result.append(Instance(**item))
            except Exception as e:
                logger.warning("Failed to parse instance item %s: %s", item.get("id"), e)
        return result

    async def get_instance(self, instance_id: int) -> Optional[Instance]:
        """Fetch details for a specific instance."""
        try:
            data = await self._request("GET", f"/api/v0/instances/{instance_id}/", params={"owner": "me"})
            inst = data.get("instances") or data
            if isinstance(inst, list) and inst:
                return Instance(**inst[0])
            elif isinstance(inst, dict):
                return Instance(**inst)
        except VastApiError as e:
            if e.status_code == 404:
                return None
            raise
        return None

    async def search_offers(self, filters: SearchFilters, limit: int = 15) -> List[Offer]:
        """Search available GPU offers according to filters."""
        query_dict: Dict[str, Any] = {
            "verified": {"eq": True} if filters.verified_only else {},
            "external": {"eq": False},
            "rentable": {"eq": True},
            "rented": {"eq": False},
        }

        if filters.gpu_name:
            query_dict["gpu_name"] = {"eq": filters.gpu_name}

        if filters.min_gpus:
            query_dict["num_gpus"] = {"gte": filters.min_gpus}
        if filters.max_gpus:
            query_dict["num_gpus"]["lte"] = filters.max_gpus

        if filters.max_dph:
            query_dict["dph_total"] = {"lte": filters.max_dph}

        if filters.min_cuda:
            query_dict["cuda_max_good"] = {"gte": filters.min_cuda}

        if filters.min_reliability:
            query_dict["reliability2"] = {"gte": filters.min_reliability}

        if filters.min_disk:
            query_dict["disk_space"] = {"gte": filters.min_disk}

        # Clean empty query dict entries
        query_dict = {k: v for k, v in query_dict.items() if v}

        params = {
            "q": json.dumps(query_dict),
            "order": [[filters.order_by, "asc"]],
            "type": "on-demand",
            "allocated_storage": filters.allocated_storage,
        }

        data = await self._request("GET", "/bundles/", params=params)
        offers_raw = data.get("offers", []) if isinstance(data, dict) else data

        offers = []
        for item in offers_raw[:limit]:
            try:
                offers.append(Offer(**item))
            except Exception as e:
                logger.debug("Skipping unparseable offer: %s", e)
        return offers

    async def create_instance(
        self,
        offer_id: int,
        image: str,
        disk_space: float = 30.0,
        onstart_cmd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        label: Optional[str] = None,
        runtype: str = "ssh",
    ) -> Dict[str, Any]:
        """
        Rent and launch a new GPU instance from an offer.
        PUT /api/v0/asks/{id}/
        """
        payload: Dict[str, Any] = {
            "client_id": "me",
            "image": image.strip(),
            "disk": disk_space,
            "runtype": runtype,
        }
        if onstart_cmd:
            payload["onstart"] = onstart_cmd
        if env:
            payload["env"] = env
        if label:
            payload["label"] = label

        return await self._request("PUT", f"/asks/{offer_id}/", json_data=payload)

    async def stop_instance(self, instance_id: int) -> Dict[str, Any]:
        """Stop an active instance (pauses billing for GPU while keeping storage)."""
        return await self._request("PUT", f"/api/v0/instances/{instance_id}/", json_data={"state": "stopped"})

    async def start_instance(self, instance_id: int) -> Dict[str, Any]:
        """Resume a stopped instance."""
        return await self._request("PUT", f"/api/v0/instances/{instance_id}/", json_data={"state": "running"})

    async def reboot_instance(self, instance_id: int) -> Dict[str, Any]:
        """Reboot an instance machine."""
        return await self._request("PUT", f"/instances/reboot/{instance_id}/", json_data={})

    async def destroy_instance(self, instance_id: int) -> Dict[str, Any]:
        """
        Immediately terminate and delete instance (Instant KILL).
        Works even when Docker image is actively loading/downloading to stop burning balance.
        DELETE /api/v0/instances/{id}/
        """
        return await self._request("DELETE", f"/api/v0/instances/{instance_id}/")
