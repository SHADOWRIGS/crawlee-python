from __future__ import annotations

from datetime import UTC, datetime

import pytest

from crawlee._request import CrawleeRequestData, Request, RequestState, RequestWithLock, UserData


class TestRequestState:
    def test_values(self) -> None:
        assert RequestState.UNPROCESSED == 0
        assert RequestState.BEFORE_NAV == 1
        assert RequestState.AFTER_NAV == 2
        assert RequestState.REQUEST_HANDLER == 3
        assert RequestState.DONE == 4
        assert RequestState.ERROR_HANDLER == 5
        assert RequestState.ERROR == 6
        assert RequestState.SKIPPED == 7

    def test_is_int(self) -> None:
        assert isinstance(RequestState.DONE, int)


class TestCrawleeRequestData:
    def test_defaults(self) -> None:
        data = CrawleeRequestData()
        assert data.max_retries is None
        assert data.enqueue_strategy is None
        assert data.state == RequestState.UNPROCESSED
        assert data.session_rotation_count is None
        assert data.skip_navigation is False
        assert data.last_proxy_tier is None
        assert data.forefront is False
        assert data.crawl_depth == 0
        assert data.session_id is None

    def test_alias_deserialization(self) -> None:
        data = CrawleeRequestData(maxRetries=5, skipNavigation=True, crawlDepth=3)
        assert data.max_retries == 5
        assert data.skip_navigation is True
        assert data.crawl_depth == 3


class TestUserData:
    def test_empty(self) -> None:
        ud = UserData()
        assert len(ud) == 0
        assert ud.label is None
        assert ud.crawlee_data is None

    def test_getitem_setitem(self) -> None:
        ud = UserData()
        ud['key'] = 'value'
        assert ud['key'] == 'value'
        assert len(ud) == 1

    def test_delitem(self) -> None:
        ud = UserData()
        ud['key'] = 'value'
        del ud['key']
        assert len(ud) == 0

    def test_missing_key_raises(self) -> None:
        ud = UserData()
        with pytest.raises(KeyError):
            _ = ud['nonexistent']

    def test_iteration(self) -> None:
        ud = UserData()
        ud['a'] = 1
        ud['b'] = 2
        keys = list(ud)
        assert 'a' in keys
        assert 'b' in keys

    def test_label_via_setitem(self) -> None:
        ud = UserData()
        ud['label'] = 'test_label'
        assert ud.label == 'test_label'

    def test_label_setitem_validation(self) -> None:
        ud = UserData()
        with pytest.raises(ValueError, match='`label` must be str or None'):
            ud['label'] = 123  # type: ignore[assignment]

    def test_label_none_via_setitem(self) -> None:
        ud = UserData()
        ud['label'] = 'test'
        ud['label'] = None
        assert ud.label is None

    def test_equality_with_dict(self) -> None:
        ud = UserData()
        ud['x'] = 42
        assert ud == ud.model_dump()

    def test_equality_with_incompatible_type(self) -> None:
        ud = UserData()
        assert ud.__eq__('not_a_dict') is NotImplemented

    def test_hash(self) -> None:
        ud1 = UserData()
        ud1['key'] = 'value'
        ud2 = UserData()
        ud2['key'] = 'value'
        assert hash(ud1) == hash(ud2)

    def test_hash_with_nested_data(self) -> None:
        ud = UserData()
        ud['nested'] = {'a': [1, 2, 3]}
        h = hash(ud)
        assert isinstance(h, int)


class TestRequestFromUrl:
    def test_basic_creation(self) -> None:
        request = Request.from_url('https://example.com')
        assert request.url == 'https://example.com'
        assert request.method == 'GET'
        assert request.payload is None
        assert request.unique_key is not None
        assert request.retry_count == 0
        assert request.no_retry is False
        assert request.loaded_url is None
        assert request.handled_at is None

    def test_with_label(self) -> None:
        request = Request.from_url('https://example.com', label='category')
        assert request.label == 'category'

    def test_with_method(self) -> None:
        request = Request.from_url('https://example.com', method='POST')
        assert request.method == 'POST'

    def test_with_payload_string(self) -> None:
        request = Request.from_url('https://example.com', method='POST', payload='test_data')
        assert request.payload == b'test_data'

    def test_with_payload_bytes(self) -> None:
        request = Request.from_url('https://example.com', method='POST', payload=b'binary_data')
        assert request.payload == b'binary_data'

    def test_with_headers(self) -> None:
        request = Request.from_url('https://example.com', headers={'Content-Type': 'application/json'})
        assert request.headers['Content-Type'] == 'application/json'

    def test_with_custom_unique_key(self) -> None:
        request = Request.from_url('https://example.com', unique_key='custom_key')
        assert request.unique_key == 'custom_key'

    def test_always_enqueue_with_unique_key_raises(self) -> None:
        with pytest.raises(ValueError, match='`always_enqueue` cannot be used with a custom `unique_key`'):
            Request.from_url('https://example.com', unique_key='my_key', always_enqueue=True)

    def test_always_enqueue_generates_unique_key(self) -> None:
        r1 = Request.from_url('https://example.com', always_enqueue=True)
        r2 = Request.from_url('https://example.com', always_enqueue=True)
        assert r1.unique_key != r2.unique_key

    def test_session_id(self) -> None:
        request = Request.from_url('https://example.com', session_id='sess_123')
        assert request.session_id == 'sess_123'

    def test_max_retries(self) -> None:
        request = Request.from_url('https://example.com', max_retries=5)
        assert request.max_retries == 5

    def test_enqueue_strategy(self) -> None:
        request = Request.from_url('https://example.com', enqueue_strategy='same-domain')
        assert request.enqueue_strategy == 'same-domain'

    def test_no_retry(self) -> None:
        request = Request.from_url('https://example.com', no_retry=True)
        assert request.no_retry is True


class TestRequestProperties:
    def test_label_property(self) -> None:
        request = Request.from_url('https://example.com', label='test')
        assert request.label == 'test'

    def test_label_none(self) -> None:
        request = Request.from_url('https://example.com')
        assert request.label is None

    def test_state_property(self) -> None:
        request = Request.from_url('https://example.com')
        assert request.state == RequestState.UNPROCESSED
        request.state = RequestState.DONE
        assert request.state == RequestState.DONE

    def test_crawl_depth(self) -> None:
        request = Request.from_url('https://example.com')
        assert request.crawl_depth == 0
        request.crawl_depth = 3
        assert request.crawl_depth == 3

    def test_forefront(self) -> None:
        request = Request.from_url('https://example.com')
        assert request.forefront is False
        request.forefront = True
        assert request.forefront is True

    def test_last_proxy_tier(self) -> None:
        request = Request.from_url('https://example.com')
        assert request.last_proxy_tier is None
        request.last_proxy_tier = 2
        assert request.last_proxy_tier == 2

    def test_session_rotation_count(self) -> None:
        request = Request.from_url('https://example.com')
        assert request.session_rotation_count is None
        request.session_rotation_count = 3
        assert request.session_rotation_count == 3

    def test_enqueue_strategy_default(self) -> None:
        request = Request.from_url('https://example.com')
        assert request.enqueue_strategy == 'all'

    def test_enqueue_strategy_setter(self) -> None:
        request = Request.from_url('https://example.com')
        request.enqueue_strategy = 'same-hostname'
        assert request.enqueue_strategy == 'same-hostname'

    def test_was_already_handled(self) -> None:
        request = Request.from_url('https://example.com')
        assert request.was_already_handled is False
        request.handled_at = datetime.now(tz=UTC)
        assert request.was_already_handled is True

    def test_get_query_param_from_url(self) -> None:
        request = Request.from_url('https://example.com?page=5&sort=asc')
        assert request.get_query_param_from_url('page') == '5'
        assert request.get_query_param_from_url('sort') == 'asc'
        assert request.get_query_param_from_url('missing') is None
        assert request.get_query_param_from_url('missing', default='fallback') == 'fallback'

    def test_crawlee_data_lazy_init(self) -> None:
        request = Request.from_url('https://example.com')
        data = request.crawlee_data
        assert isinstance(data, CrawleeRequestData)


class TestRequestSerialization:
    def test_roundtrip(self) -> None:
        request = Request.from_url(
            'https://example.com',
            label='test',
            method='POST',
            payload='body',
        )
        data = request.model_dump(by_alias=True)
        restored = Request.model_validate(data)
        assert restored.url == request.url
        assert restored.method == request.method
        assert restored.unique_key == request.unique_key
        assert restored.label == request.label

    def test_json_roundtrip(self) -> None:
        request = Request.from_url('https://example.com', label='json_test')
        json_str = request.model_dump_json(by_alias=True)
        restored = Request.model_validate_json(json_str)
        assert restored.url == request.url
        assert restored.label == request.label


class TestRequestWithLock:
    def test_creation(self) -> None:
        now = datetime.now(tz=UTC)
        req = RequestWithLock(
            url='https://example.com',
            unique_key='test_key',
            lock_expires_at=now,
        )
        assert req.lock_expires_at == now
        assert req.url == 'https://example.com'
