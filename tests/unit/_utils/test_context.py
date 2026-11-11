from __future__ import annotations

import pytest

from crawlee._utils.context import ensure_context


class TestEnsureContext:
    def test_sync_active(self) -> None:
        class MyService:
            active = True

            @ensure_context
            def do_work(self) -> str:
                return 'done'

        svc = MyService()
        assert svc.do_work() == 'done'

    def test_sync_inactive_raises(self) -> None:
        class MyService:
            active = False

            @ensure_context
            def do_work(self) -> str:
                return 'done'

        svc = MyService()
        with pytest.raises(RuntimeError, match='is not active'):
            svc.do_work()

    def test_sync_no_active_attr_raises(self) -> None:
        class MyService:
            @ensure_context
            def do_work(self) -> str:
                return 'done'

        svc = MyService()
        with pytest.raises(RuntimeError, match='does not have the "active" attribute'):
            svc.do_work()

    async def test_async_active(self) -> None:
        class MyService:
            active = True

            @ensure_context
            async def do_work(self) -> str:
                return 'done'

        svc = MyService()
        result = await svc.do_work()
        assert result == 'done'

    async def test_async_inactive_raises(self) -> None:
        class MyService:
            active = False

            @ensure_context
            async def do_work(self) -> str:
                return 'done'

        svc = MyService()
        with pytest.raises(RuntimeError, match='is not active'):
            await svc.do_work()

    async def test_async_no_active_attr_raises(self) -> None:
        class MyService:
            @ensure_context
            async def do_work(self) -> str:
                return 'done'

        svc = MyService()
        with pytest.raises(RuntimeError, match='does not have the "active" attribute'):
            await svc.do_work()
