import logging
import time
from typing import Any, Optional

import httpx

logger = logging.getLogger("ms-client")


class CircuitOpenError(Exception):
    """Состояние OPEN: запросы к сервису временно запрещены."""


class CircuitBreaker:
    """Автоматический выключатель: CLOSED → OPEN → HALF-OPEN → CLOSED/OPEN."""

    def __init__(self, failure_threshold: int = 3, open_timeout: float = 2.0):
        self.failure_threshold = failure_threshold
        self.open_timeout = open_timeout
        self.failures = 0
        self.state = "CLOSED"
        self.opened_at = 0.0

    def allow(self) -> bool:
        if self.state == "OPEN":
            if time.monotonic() - self.opened_at >= self.open_timeout:
                self.state = "HALF-OPEN"
                return True
            return False
        return True

    def success(self) -> None:
        self.failures = 0
        self.state = "CLOSED"

    def failure(self) -> None:
        self.failures += 1
        if self.state == "HALF-OPEN" or self.failures >= self.failure_threshold:
            self.state = "OPEN"
            self.opened_at = time.monotonic()

    def __repr__(self) -> str:
        return f"CircuitBreaker(state={self.state}, failures={self.failures})"


class ServiceClient:
    """HTTP-клиент с паттернами Retry и Circuit Breaker."""

    RETRYABLE_STATUS = {503, 504}

    def __init__(self, base_url: str, retries: int = 3, backoff: float = 0.15,
                 breaker: Optional[CircuitBreaker] = None):
        self.base_url = base_url.rstrip("/")
        self.retries = retries
        self.backoff = backoff
        self.breaker = breaker or CircuitBreaker()

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path: str) -> Any:
        if not self.breaker.allow():
            raise CircuitOpenError("Сервис недоступен (Circuit Breaker OPEN)")

        last_error: Optional[Exception] = None
        for attempt in range(1, self.retries + 1):
            try:
                response = httpx.get(self._url(path), timeout=1.0)
                if response.status_code in self.RETRYABLE_STATUS:
                    raise httpx.HTTPStatusError(
                        f"Временная ошибка: {response.status_code}", request=response.request,
                        response=response,
                    )
                response.raise_for_status()
                self.breaker.success()
                return response.json()
            except (httpx.HTTPStatusError, httpx.ConnectError) as error:
                last_error = error
                logger.warning("Попытка %d/%d к %s не удалась: %s",
                               attempt, self.retries, path, error)
                if attempt < self.retries:
                    time.sleep(self.backoff * attempt)
        self.breaker.failure()
        raise last_error or RuntimeError("Сервис недоступен")

    def breaker_state(self) -> str:
        return self.breaker.state