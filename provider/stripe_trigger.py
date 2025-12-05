import json
import logging
import time
from collections.abc import Mapping
from typing import Any

import stripe
from dify_plugin.entities.provider_config import CredentialType
from dify_plugin.entities.trigger import EventDispatch, Subscription, UnsubscribeResult
from dify_plugin.errors.trigger import (
    TriggerDispatchError,
    TriggerProviderCredentialValidationError,
    TriggerValidationError,
)
from dify_plugin.interfaces.trigger import Trigger, TriggerSubscriptionConstructor
from stripe import Event as StripeEvent
from werkzeug import Request, Response


class StripeTriggerTrigger(Trigger):
    """
    Handle the webhook event dispatch.
    """

    def _dispatch_event(self, subscription: Subscription, request: Request) -> EventDispatch:
        endpoint_secret = subscription.properties.get("endpoint_secret")
        stripe_event: StripeEvent = self._parse_and_validate_payload(request, endpoint_secret)
        payload: Mapping[str, Any] = {
            "stripe_event": stripe_event,
        }

        event_names: list[str] = self._dispatch_trigger_events(stripe_event=stripe_event)

        response_object = {
            "status": "ok",
            "event_type": stripe_event.type,
            "dispatched_event_names": event_names,
        }
        response = Response(response=json.dumps(response_object), status=200, mimetype="application/json")
        return EventDispatch(events=event_names, response=response, payload=payload)

    def _dispatch_trigger_events(self, stripe_event: StripeEvent) -> list[str]:
        """Dispatch events based on webhook payload."""
        # # Get the event type from the payload
        # event_type = stripe_event.type
        # event_type = event_type.replace(".", "_")

        # todo: support thin events
        events = ["stripe_snapshot_events"]

        return events

    def _parse_payload(self, request: Request) -> Mapping[str, Any]:
        try:
            payload = request.get_json(force=True)
            if not payload:
                raise TriggerDispatchError("Empty request body")
            return payload
        except TriggerDispatchError:
            raise
        except Exception as exc:
            raise TriggerDispatchError(f"Failed to parse payload: {exc}") from exc

    def _parse_and_validate_payload(self, request: Request, endpoint_secret: str):
        sig_header = request.headers.get('Stripe-Signature', "")
        try:
            event: StripeEvent = stripe.Webhook.construct_event(
                payload=request.data, sig_header=sig_header, secret=endpoint_secret
                # todo: optional api_key
            )
            return event
        except stripe.error.SignatureVerificationError as e:
            logging.exception(e)
            raise TriggerValidationError(
                f"Failed to verify webhook signature,"
                f" webhook secret len: {len(endpoint_secret)},",
                f" signature header len: {len(sig_header)},",
                f" exception: {str(e)}")


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
