"""Tests for quart_github_webhook.webhook"""

import pytest
import json
import quart
import contextlib

try:
    from unittest import mock
except ImportError:
    import mock

from quart_github_webhook.webhook import Webhook


@contextlib.asynccontextmanager
async def mock_request(app, **opts):
    opts.setdefault('headers', {}).setdefault("X-Github-Delivery", "")
    async with app.test_request_context(
        path='/postreceive',
        method='POST',
        **opts,
    ) as reqctx:
        yield mock.MagicMock(reqctx.request)


@contextlib.asynccontextmanager
async def push_request(app, **opts):
    opts.setdefault('data', b"{}")
    opts.setdefault('headers', {}).setdefault("X-Github-Event", "push")
    opts.setdefault('headers', {}).setdefault("content-type", "application/json")
    async with mock_request(app, **opts) as req:
        yield req


@contextlib.asynccontextmanager
async def push_request_encoded(app, **opts):
    opts.setdefault('data', "payload=%7B%7D")
    opts.setdefault('headers', {}).setdefault("X-Github-Event", "push")
    opts.setdefault('headers', {}).setdefault("content-type", "application/x-www-form-urlencoded")
    async with mock_request(app, **opts) as req:
        yield req


@pytest.fixture
def app():
    yield quart.Quart(__name__)


@pytest.fixture
def webhook(app):
    yield Webhook(app)


@pytest.fixture
def handler(webhook):
    handler = mock.AsyncMock()
    webhook.hook("push")(handler)
    yield handler


def test_constructor():
    # GIVEN
    app = mock.Mock()

    # WHEN
    webhook = Webhook(app)

    # THEN
    app.add_url_rule.assert_called_once_with(
        endpoint="/postreceive", path="/postreceive", view_func=webhook._postreceive, methods=["POST"]
    )


@pytest.mark.asyncio
async def test_run_push_hook(app, webhook, handler):
    async with push_request(app):
        # WHEN
        await webhook._postreceive()

        # THEN
        # handler.assert_called_once_with(req.get_json.return_value)
        handler.assert_called_once()


@pytest.mark.asyncio
async def test_run_push_hook_urlencoded(app, webhook, handler):
    async with push_request_encoded(app):

        # WHEN
        await webhook._postreceive()

        # THEN
        # handler.assert_called_once_with(payload)
        handler.assert_called_once()


@pytest.mark.asyncio
async def test_do_not_run_push_hook_on_ping(app, webhook, handler):
    # GIVEN
    async with mock_request(app, data="{}", headers={
        "X-Github-Event": "ping",
        "content-type": "application/json",
    }):
        # WHEN
        await webhook._postreceive()

        # THEN
        handler.assert_not_called()


@pytest.mark.asyncio
async def test_do_not_run_push_hook_on_ping_urlencoded(app, webhook, handler):
    # GIVEN
    async with mock_request(app, data="payload={}", headers={
        "X-Github-Event": "ping",
        "content-type": "application/x-www-form-urlencoded",
    }):
        # WHEN
        await webhook._postreceive()

        # THEN
        handler.assert_not_called()


@pytest.mark.asyncio
async def test_can_handle_zero_events(app, webhook):
    async with push_request(app):
        # WHEN, THEN
        await webhook._postreceive()  # noop


@pytest.mark.asyncio
@pytest.mark.parametrize("secret", [u"secret", b"secret"])
@mock.patch("quart_github_webhook.webhook.hmac")
async def test_calls_if_signature_is_correct(mock_hmac, app, secret):
    # GIVEN
    webhook = Webhook(app, secret=secret)
    async with push_request(app, headers={"X-Hub-Signature": "sha1=hash_of_something"}):
        handler = mock.AsyncMock()
        mock_hmac.compare_digest.return_value = True

        # WHEN
        webhook.hook("push")(handler)
        await webhook._postreceive()

        # THEN
        # handler.assert_called_once_with(push_request.get_json.return_value)
        handler.assert_called_once()


@pytest.mark.asyncio
@mock.patch("quart_github_webhook.webhook.hmac")
async def test_does_not_call_if_signature_is_incorrect(mock_hmac, app):
    # GIVEN
    webhook = Webhook(app, secret="super_secret")
    async with push_request(app, headers={"X-Hub-Signature": "sha1=hash_of_something"}):
        handler = mock.Mock()
        mock_hmac.compare_digest.return_value = False

        # WHEN, THEN
        webhook.hook("push")(handler)
        with pytest.raises(quart.exceptions.BadRequest):
            await webhook._postreceive()


@pytest.mark.asyncio
async def test_request_has_no_data(app, webhook, handler):
    # GIVEN
    async with push_request(app, data=""):
        # WHEN, THEN
        with pytest.raises(quart.exceptions.BadRequest):
            await webhook._postreceive()


@pytest.mark.asyncio
async def test_request_had_headers(app, webhook, handler):
    # WHEN, THEN
    async with mock_request(app):
        with pytest.raises(quart.exceptions.BadRequest):
            await webhook._postreceive()


# -----------------------------------------------------------------------------
# Copyright 2020 Go Build It, LLC
# Copyright 2015 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------- END-OF-FILE -----------------------------------
