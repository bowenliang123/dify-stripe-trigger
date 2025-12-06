import json
import time
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from dify_plugin.entities.provider_config import CredentialType
from dify_plugin.entities.trigger import EventDispatch, Subscription, UnsubscribeResult
from dify_plugin.errors.trigger import (
    TriggerProviderCredentialValidationError, TriggerValidationError,
)
from dify_plugin.interfaces.trigger import Trigger, TriggerSubscriptionConstructor
from werkzeug import Request, Response


class StripeTriggerTrigger(Trigger):
    """
    Handle the webhook event dispatch.
    """

    def _dispatch_event(self, subscription: Subscription, request: Request) -> EventDispatch:
        # endpoint_secret = subscription.properties.get("endpoint_secret")
        request_json = request.get_json(silent=True) or {}
        event_type = request_json.get("type", "")
        if not event_type:
            raise TriggerValidationError("The event type is empty")
        is_thin_event = event_type.startswith("v")

        event_names: list[str] = self._dispatch_trigger_events(is_thin_event=is_thin_event)
        payload = {
            "is_thin_event": is_thin_event,
        }

        # print(f"request_json: {request_json}")
        # print(f"payload: {payload}")
        # print(f"is_thin_event: {is_thin_event}")
        # print(f"triggered_event_names: {event_names}")

        response_object = {
            "status": "ok",
            "event_type": event_type,
            "triggered_event_names": event_names,
            "timestamp": datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        }
        response = Response(response=json.dumps(response_object), status=200, mimetype="application/json")
        return EventDispatch(events=event_names, response=response, payload=payload)

    def _dispatch_trigger_events(self, is_thin_event: bool) -> list[str]:
        """Dispatch events based on webhook payload."""
        if is_thin_event:
            events = ["stripe_thin_events"]
        else:
            events = ["stripe_snapshot_events"]
        return events


class StripeTriggerSubscriptionConstructor(TriggerSubscriptionConstructor):
    """Manage stripe_trigger trigger subscriptions."""

    def _validate_api_key(self, credentials: dict[str, Any]) -> None:
        api_key = credentials.get("api_key")
        if not api_key:
            raise TriggerProviderCredentialValidationError("API key is required to validate credentials.")

    def _create_subscription(
            self,
            endpoint: str,
            parameters: Mapping[str, Any],
            credentials: Mapping[str, Any],
            credential_type: CredentialType,
    ) -> Subscription:
        events: list[str] = parameters.get("events", [])

        # Replace this placeholder with API calls to register a webhook
        return Subscription(
            expires_at=int(time.time()) + 7 * 24 * 60 * 60,
            endpoint=endpoint,
            properties={
                "external_id": "example-subscription",
                "events": events,
            },
        )

    def _delete_subscription(
            self,
            subscription: Subscription,
            credentials: Mapping[str, Any],
            credential_type: CredentialType,
    ) -> UnsubscribeResult:
        # Tear down any remote subscription that was created in `_subscribe`.
        return UnsubscribeResult(success=True, message="Subscription removed.")

    def _refresh_subscription(
            self,
            subscription: Subscription,
            credentials: Mapping[str, Any],
            credential_type: CredentialType,
    ) -> Subscription:
        # Extend the subscription lifetime or renew tokens with your upstream service.
        return Subscription(
            expires_at=int(time.time()) + 7 * 24 * 60 * 60,
            endpoint=subscription.endpoint,
            properties=subscription.properties,
        )
