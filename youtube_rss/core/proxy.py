import httpx
from fastapi.requests import Request
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

client = httpx.AsyncClient()


async def reverse_proxy(url: str, request: Request) -> StreamingResponse:
    url = httpx.URL(url=url)

    rp_req = client.build_request(method=request.method, headers=request.headers, url=url)
    rp_resp = await client.send(rp_req, stream=True)

    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=rp_resp.headers,
        background=BackgroundTask(rp_resp.aclose),
    )
