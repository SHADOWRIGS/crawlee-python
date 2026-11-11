from __future__ import annotations

from datetime import timedelta

from pydantic import BaseModel

from crawlee._utils.models import (
    _timedelta_from_ms,
    _timedelta_from_secs,
    _timedelta_to_ms,
    _timedelta_to_secs,
    timedelta_ms,
    timedelta_secs,
)


class TestTimedeltaToMs:
    def test_normal_value(self) -> None:
        assert _timedelta_to_ms(timedelta(seconds=1)) == 1000

    def test_none(self) -> None:
        assert _timedelta_to_ms(None) is None

    def test_max(self) -> None:
        assert _timedelta_to_ms(timedelta.max) == float('inf')

    def test_fractional(self) -> None:
        assert _timedelta_to_ms(timedelta(milliseconds=500)) == 500


class TestTimedeltaToSecs:
    def test_normal_value(self) -> None:
        assert _timedelta_to_secs(timedelta(seconds=5)) == 5.0

    def test_none(self) -> None:
        assert _timedelta_to_secs(None) is None

    def test_max(self) -> None:
        assert _timedelta_to_secs(timedelta.max) == float('inf')


class TestTimedeltaFromMs:
    def test_from_int(self) -> None:
        result = _timedelta_from_ms(1000, timedelta)
        assert result == timedelta(seconds=1)

    def test_from_float(self) -> None:
        result = _timedelta_from_ms(500.0, timedelta)
        assert result == timedelta(milliseconds=500)

    def test_from_inf(self) -> None:
        result = _timedelta_from_ms(float('inf'), timedelta)
        assert result == timedelta.max

    def test_from_string_number(self) -> None:
        result = _timedelta_from_ms('2000', timedelta)
        assert result == timedelta(seconds=2)

    def test_from_timedelta(self) -> None:
        td = timedelta(seconds=3)
        handler = lambda v: v  # noqa: E731
        result = _timedelta_from_ms(td, handler)
        assert result == td


class TestTimedeltaFromSecs:
    def test_from_int(self) -> None:
        result = _timedelta_from_secs(5, timedelta)
        assert result == timedelta(seconds=5)

    def test_from_inf(self) -> None:
        result = _timedelta_from_secs(float('inf'), timedelta)
        assert result == timedelta.max

    def test_from_string_number(self) -> None:
        result = _timedelta_from_secs('10', timedelta)
        assert result == timedelta(seconds=10)


class TestTimedeltaMsAnnotation:
    def test_pydantic_model_roundtrip(self) -> None:
        class MyModel(BaseModel):
            duration: timedelta_ms

        m = MyModel(duration=timedelta(seconds=2))
        data = m.model_dump()
        assert data['duration'] == 2000

    def test_pydantic_model_from_ms_value(self) -> None:
        class MyModel(BaseModel):
            duration: timedelta_ms

        m = MyModel.model_validate({'duration': 3000})
        assert m.duration == timedelta(seconds=3)


class TestTimedeltaSecsAnnotation:
    def test_pydantic_model_roundtrip(self) -> None:
        class MyModel(BaseModel):
            duration: timedelta_secs

        m = MyModel(duration=timedelta(seconds=5))
        data = m.model_dump()
        assert data['duration'] == 5.0

    def test_pydantic_model_from_secs_value(self) -> None:
        class MyModel(BaseModel):
            duration: timedelta_secs

        m = MyModel.model_validate({'duration': 10})
        assert m.duration == timedelta(seconds=10)
