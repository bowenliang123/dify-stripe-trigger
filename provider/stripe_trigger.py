import logging
import time
from collections.abc import Mapping
from typing import Any

from werkzeug import Request, Response

from dify_plugin.entities.oauth import TriggerOAuthCredentials
from dify_plugin.entities.provider_config import CredentialType
from dify_plugin.entities.trigger import EventDispatch, Subscription, UnsubscribeResult
from dify_plugin.errors.trigger import (
    SubscriptionError,
    TriggerDispatchError,
    TriggerProviderCredentialValidationError,
    TriggerProviderOAuthError,
    UnsubscribeError,
)
from dify_plugin.interfaces.trigger import Trigger, TriggerSubscriptionConstructor
import stripe


class StripeTriggerTrigger(Trigger):
    """
    Handle the webhook event dispatch.
    """

    def _dispatch_event(self, subscription: Subscription, request: Request) -> EventDispatch:
        endpoint_secret = subscription.properties.get("endpoint_secret")
        stripe_event: stripe.Event = self._parse_and_validate_payload(request, endpoint_secret)
        payload: Mapping[str, Any] = {
            "stripe_event": stripe_event
        }
        response = Response(response='{"status": "ok"}', status=200, mimetype="application/json")

        events: list[str] = self._dispatch_trigger_events(stripe_event=stripe_event)

        return EventDispatch(events=events, response=response, payload=payload)

    def _dispatch_trigger_events(self, stripe_event: stripe.Event) -> list[str]:
        """Dispatch events based on webhook payload."""
        # Get the event type from the payload
        event_type = stripe_event.type
        event_type = event_type.replace(".", "_")

        events = [event_type]
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
        payload = self._parse_payload(request)
        sig_header = request.headers.get('HTTP_STRIPE_SIGNATURE', "")
        try:
            event: stripe.Event = stripe.Webhook.construct_event(
                payload=payload, sig_header=sig_header, secret=endpoint_secret
                # todo: optional api_key
            )
            return event
        except stripe.error.SignatureVerificationError as e:
            logging.exception(e)
            raise TriggerProviderOAuthError(
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
