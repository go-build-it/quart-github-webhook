"""Tests for quart_github_webhook.webhook"""

from __future__ import print_function

import pytest
import json
import quart

try:
    from unittest import mock
except ImportError:
    import mock

from quart_github_webhook.webhook import Webhook


@pytest.fixture
async def mock_request(app):
    async with app.test_request_context(
        path='/postreceive',
        method='POST',
        headers={"X-Github-Delivery": ""},
    ) as reqctx:
        yield reqctx.request


@pytest.fixture
def push_request(mock_request):
    mock_request.headers["X-Github-Event"] = "push"
    mock_request.headers["content-type"] = "application/json"
    yield mock_request


@pytest.fixture
def push_request_encoded(mock_request):
    mock_request.headers["X-Github-Event"] = "push"
    mock_request.headers["content-type"] = "application/x-www-form-urlencoded"
    yield mock_request


@pytest.fixture
def app():
    yield mock.MagicMock(quart.Quart(__name__))


@pytest.fixture
def webhook(app):
    yield Webhook(app)


@pytest.fixture
def handler(webhook):
    handler = mock.AsyncMock()
    webhook.hook()(handler)
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
async def test_run_push_hook(webhook, handler, push_request):
    # WHEN
    await webhook._postreceive()

    # THEN
    handler.assert_called_once_with(push_request.get_json.return_value)


@pytest.mark.asyncio
async def test_run_push_hook_urlencoded(webhook, handler, push_request_encoded):
    github_mock_payload = {"payload": '{"key": "value"}'}
    push_request_encoded.form.to_dict.return_value = github_mock_payload
    payload = json.loads(github_mock_payload["payload"])

    # WHEN
    await webhook._postreceive()

    # THEN
    handler.assert_called_once_with(payload)


@pytest.mark.asyncio
async def test_do_not_run_push_hook_on_ping(webhook, handler, mock_request):
    # GIVEN
    mock_request.headers["X-Github-Event"] = "ping"
    mock_request.headers["content-type"] = "application/json"

    # WHEN
    await webhook._postreceive()

    # THEN
    handler.assert_not_called()


@pytest.mark.asyncio
async def test_do_not_run_push_hook_on_ping_urlencoded(webhook, handler, mock_request):
    # GIVEN
    mock_request.headers["X-Github-Event"] = "ping"
    mock_request.headers["content-type"] = "application/x-www-form-urlencoded"
    mock_request.form.to_dict.return_value = {"payload": '{"key": "value"}'}

    # WHEN
    await webhook._postreceive()

    # THEN
    handler.assert_not_called()


@pytest.mark.asyncio
async def test_can_handle_zero_events(webhook, push_request):
    # WHEN, THEN
    await webhook._postreceive()  # noop


@pytest.mark.asyncio
@pytest.mark.parametrize("secret", [u"secret", b"secret"])
@mock.patch("quart_github_webhook.webhook.hmac")
async def test_calls_if_signature_is_correct(mock_hmac, app, push_request, secret):
    # GIVEN
    webhook = Webhook(app, secret=secret)
    push_request.headers["X-Hub-Signature"] = "sha1=hash_of_something"
    push_request.data = b"something"
    handler = mock.Mock()
    mock_hmac.compare_digest.return_value = True

    # WHEN
    webhook.hook()(handler)
    await webhook._postreceive()

    # THEN
    handler.assert_called_once_with(push_request.get_json.return_value)


@pytest.mark.asyncio
@mock.patch("quart_github_webhook.webhook.hmac")
async def test_does_not_call_if_signature_is_incorrect(mock_hmac, app, push_request):
    # GIVEN
    webhook = Webhook(app, secret="super_secret")
    push_request.headers["X-Hub-Signature"] = "sha1=hash_of_something"
    push_request.data = b"something"
    handler = mock.Mock()
    mock_hmac.compare_digest.return_value = False

    # WHEN, THEN
    webhook.hook()(handler)
    with pytest.raises(quart.exceptions.BadRequest):
        await webhook._postreceive()


@pytest.mark.asyncio
async def test_request_has_no_data(webhook, handler, push_request):
    # GIVEN
    push_request.get_json.return_value = None

    # WHEN, THEN
    with pytest.raises(quart.exceptions.BadRequest):
        await webhook._postreceive()


@pytest.mark.asyncio
async def test_request_had_headers(webhook, handler, mock_request):
    # WHEN, THEN
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
