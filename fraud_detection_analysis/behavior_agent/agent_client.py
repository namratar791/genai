import asyncio
from uuid import uuid4

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential


def is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500
    return isinstance(
        exc,
        (
            httpx.ConnectError,
            httpx.ReadTimeout,
            httpx.RemoteProtocolError,
            asyncio.TimeoutError,
        ),
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception(is_retryable),
    reraise=True,
)
async def post_json(*, url: str, payload: dict, timeout_seconds: float = 10.0) -> dict:
    async def _do_call() -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=timeout_seconds)
            response.raise_for_status()
            return response.json()

    return await asyncio.wait_for(_do_call(), timeout=timeout_seconds + 1)


async def post_a2a_task(
    *,
    url: str,
    payload: dict,
    requested_skill: str,
    from_agent: str,
    timeout_seconds: float = 10.0,
) -> dict:
    task_envelope = {
        "task_id": str(uuid4()),
        "message": {
            "role": "user",
            "parts": [{"type": "json", "data": payload}],
        },
        "metadata": {
            "from_agent": from_agent,
            "requested_skill": requested_skill,
        },
    }
    response = await post_json(url=url, payload=task_envelope, timeout_seconds=timeout_seconds)
    return response.get("result", response)
