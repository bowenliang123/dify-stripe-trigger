import logging
from collections.abc import Mapping
from typing import Any

from dify_plugin.entities.trigger import Variables
from dify_plugin.errors.trigger import (
    TriggerDispatchError,
)
from dify_plugin.errors.trigger import TriggerValidationError
from dify_plugin.interfaces.trigger import Event
from stripe import Event as StripeEvent
from stripe import StripeClient
from werkzeug import Request

from common.http_headers import HEADER_STRIPE_SIGNATURE


class StripeThinEvents(Event):
    """
    Doc of thin events:
    https://docs.stripe.com/api/v2/core/events
    """

    def _on_event(self, request: Request, parameters: Mapping[str, Any], payload: Mapping[str, Any]) -> Variables:
        signing_secret = parameters.get("signing_secret", "")
        if not signing_secret:
            raise TriggerValidationError("The parameter singing secret is empty")

        api_key = parameters.get("api_key")
        if not api_key:
            raise TriggerValidationError("The parameter api key is empty")

        stripe_event: StripeEvent = self._parse_and_validate_payload(request, signing_secret, api_key)
        if not stripe_event:
            raise TriggerValidationError("No Stripe snapshot event parsed from the payload.")

        # generate from retrieved event (instead of thin event)
        return Variables(variables={**stripe_event})

    def _parse_and_validate_payload(self, request: Request, signing_secret: str, api_key: str):
        client = StripeClient(api_key=api_key)
        sig_header = request.headers.get(HEADER_STRIPE_SIGNATURE, "")
        try:
            # Parse the thin event notification
            event_notification = client.parse_event_notification(request.data, sig_header, signing_secret)
            if not event_notification:
                raise TriggerDispatchError("Empty event notification")
            # print(f"event_notification: {event_notification}")

            # Retrieve the full event using the event ID from the notification
            event = client.v2.core.events.retrieve(event_notification.id)
            # print(f"event v2: {event}")

            return event
        except Exception as e:
            logging.exception(e)
            raise TriggerValidationError(
                f"Failed to verify Strip thin event payload's webhook signature,"
                f" signing secret length: {len(signing_secret)},"
                f" signature header length: {len(sig_header)},"
                f" Exception: {str(e)}")
