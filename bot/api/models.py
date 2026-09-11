from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Offer(BaseModel):
    id: int
    machine_id: Optional[int] = None
    gpu_name: str = Field(default="Unknown GPU")
    num_gpus: int = Field(default=1)
    gpu_ram: float = Field(default=0.0)  # In MB or GB depending on field
    total_flops: Optional[float] = None
    dlperf: Optional[float] = None
    dlperf_per_dphtotal: Optional[float] = None
    dph_total: float = Field(default=0.0)  # Dollar per hour total
    dph_base: Optional[float] = None
    reliability: Optional[float] = None
    reliability2: Optional[float] = None
    inet_down: Optional[float] = None  # Mbps
    inet_up: Optional[float] = None    # Mbps
    inet_down_cost: Optional[float] = None
    inet_up_cost: Optional[float] = None
    cpu_name: Optional[str] = None
    cpu_cores: Optional[int] = None
    cpu_cores_effective: Optional[float] = None
    cpu_ram: Optional[float] = None  # MB
    disk_space: Optional[float] = None  # GB
    cuda_max_good: Optional[float] = None
    direct_port_count: Optional[int] = None
    geolocation: Optional[str] = None
    verified: Optional[bool] = False
    static_ip: Optional[bool] = False
    storage_cost: Optional[float] = None  # $/GB/month

    @property
    def formatted_gpu_ram_gb(self) -> str:
        # Vast.ai usually returns gpu_ram in MB
        if self.gpu_ram > 512:
            return f"{self.gpu_ram / 1024:.0f} GB"
        return f"{self.gpu_ram:.0f} GB"

    @property
    def formatted_cpu_ram_gb(self) -> str:
        if self.cpu_ram:
            if self.cpu_ram > 512:
                return f"{self.cpu_ram / 1024:.0f} GB"
            return f"{self.cpu_ram:.0f} GB"
        return "N/A"

    @property
    def reliability_percent(self) -> str:
        rel = self.reliability2 if self.reliability2 is not None else self.reliability
        if rel is not None:
            return f"{rel * 100:.1f}%"
        return "N/A"


class Instance(BaseModel):
    id: int
    machine_id: Optional[int] = None
    actual_status: str = Field(default="offline")
    intended_status: Optional[str] = None
    cur_state: Optional[str] = None
    next_state: Optional[str] = None
    status_msg: Optional[str] = None
    gpu_name: str = Field(default="Unknown GPU")
    num_gpus: int = Field(default=1)
    gpu_ram: float = Field(default=0.0)
    cpu_cores: Optional[int] = None
    cpu_ram: Optional[float] = None
    disk_space: Optional[float] = None
    dph_total: float = Field(default=0.0)
    ssh_host: Optional[str] = None
    ssh_port: Optional[int] = None
    direct_port_start: Optional[int] = None
    direct_port_end: Optional[int] = None
    image_uuid: Optional[str] = None
    image_runtype: Optional[str] = None
    label: Optional[str] = None
    start_date: Optional[float] = None
    duration: Optional[float] = None
    is_bid: Optional[bool] = False
    reliability: Optional[float] = None
    geolocation: Optional[str] = None

    @property
    def is_loading(self) -> bool:
        """Check if the instance is currently pulling or loading Docker image."""
        status = (self.actual_status or "").lower()
        msg = (self.status_msg or "").lower()
        cur = (self.cur_state or "").lower()
        return (
            status in ["loading", "downloading", "creating", "starting"]
            or "pulling" in msg
            or "download" in msg
            or "extracting" in msg
            or cur in ["loading", "downloading"]
        )

    @property
    def is_running(self) -> bool:
        return (self.actual_status or "").lower() == "running"

    @property
    def is_stopped(self) -> bool:
        return (self.actual_status or "").lower() in ["stopped", "inactive"]

    @property
    def ssh_command(self) -> Optional[str]:
        if self.ssh_host and self.ssh_port:
            return f"ssh -p {self.ssh_port} root@{self.ssh_host} -L 8080:localhost:8080"
        return None


class UserInfo(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    balance: float = Field(default=0.0)
    credit: float = Field(default=0.0)
    total_spend: Optional[float] = None
    billed_cost: Optional[float] = None


class SearchFilters(BaseModel):
    gpu_name: Optional[str] = None
    min_gpus: int = Field(default=1, ge=1)
    max_gpus: Optional[int] = None
    max_dph: Optional[float] = None
    min_cuda: Optional[float] = None
    min_disk: Optional[float] = None
    min_reliability: Optional[float] = Field(default=0.90)
    verified_only: bool = Field(default=False)
    order_by: str = Field(default="dph_total")
    allocated_storage: float = Field(default=30.0)
