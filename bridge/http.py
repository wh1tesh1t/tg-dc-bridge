# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Elinsrc

import aiohttp
from loguru import logger


class HttpClient:
    def __init__(self, timeout: int = 15):
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: aiohttp.ClientSession | None = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None:
            raise RuntimeError("HttpClient is not started")
        return self._session

    async def start(self) -> None:
        self._session = aiohttp.ClientSession()

    async def stop(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def fetch(self, url: str, max_bytes: int | None = None) -> bytes | None:
        try:
            async with self.session.get(url, timeout=self._timeout) as r:
                if r.status == 200:
                    if max_bytes is not None:
                        if r.content_length and r.content_length > max_bytes:
                            logger.warning("Fetch {} exceeds maximum size of {} bytes", url, max_bytes)
                            return None
                        chunks: list[bytes] = []
                        size = 0
                        async for chunk in r.content.iter_chunked(64 * 1024):
                            size += len(chunk)
                            if size > max_bytes:
                                logger.warning("Fetch {} exceeds maximum size of {} bytes", url, max_bytes)
                                return None
                            chunks.append(chunk)
                        return b"".join(chunks)
                    return await r.read()
                logger.warning("Fetch {} -> HTTP {}", url, r.status)
        except Exception as e:
            logger.warning("Fetch failed: {!r}", e)
        return None
