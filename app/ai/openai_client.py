import os
from openai import AsyncOpenAI
from app.config import settings

proxy_url = os.getenv("OPENAI_PROXY_URL")

if proxy_url:
    from httpx import AsyncHTTPTransport
    import httpx

    transport = AsyncHTTPTransport(proxy=proxy_url)
    client = AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        http_client=httpx.AsyncClient(transport=transport, timeout=60.0)
    )
else:
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
