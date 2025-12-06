import logging
from collections.abc import Mapping
from typing import Any

import stripe
from dify_plugin.entities.trigger import Variables
from dify_plugin.errors.trigger import TriggerValidationError
from dify_plugin.interfaces.trigger import Event
from stripe import Event as StripeEvent
from werkzeug import Request

from common.http_headers import HEADER_STRIPE_SIGNATURE


class StripeSnapshotEvents(Event):
    """
    Doc of snapshot events:
    https://docs.stripe.com/api/events
    """

    def _on_event(self, request: Request, parameters: Mapping[str, Any], payload: Mapping[str, Any]) -> Variables:
        signing_secret = parameters.get("signing_secret", "")
        if not signing_secret:
            raise TriggerValidationError("The parameter singing secret is empty")

        stripe_event: StripeEvent = self._parse_and_validate_payload(request, signing_secret)
        if not stripe_event:
            raise TriggerValidationError("No Stripe snapshot event parsed from the payload.")

        # generate from raw json from request
        request_json = request.get_json(silent=True) or {}
        return Variables(variables={**request_json})

    def _parse_and_validate_payload(self, request: Request, signing_secret: str):
        sig_header = request.headers.get(HEADER_STRIPE_SIGNATURE, "")
        try:
            event: StripeEvent = stripe.Webhook.construct_event(
                payload=request.data,
                sig_header=sig_header,
                secret=signing_secret
            )
            return event
        except stripe.error.SignatureVerificationError as e:
            logging.exception(e)
            raise TriggerValidationError(
                f"Failed to verify Strip snapshot event payload's webhook signature,"
                f" signing secret length: {len(signing_secret)},"
                f" signature header length: {len(sig_header)},"
                f" Exception: {str(e)}")
