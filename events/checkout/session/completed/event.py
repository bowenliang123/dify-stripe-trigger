from collections.abc import Mapping
from typing import Any

from werkzeug import Request

from dify_plugin.entities.trigger import Variables
from dify_plugin.errors.trigger import EventIgnoreError
from dify_plugin.interfaces.trigger import Event
from stripe import Event as StripeEvent


class StripeCheckoutSessionCompletedEvent(Event):
    """
    Event type:
    checkout.session.completed

    Doc:
    https://docs.stripe.com/api/events/types#event_types-checkout.session.completed
    """

    def _on_event(self, request: Request, parameters: Mapping[str, Any], payload: Mapping[str, Any]) -> Variables:
        stripe_event: StripeEvent = payload.get("stripe_event")
        event_type = stripe_event.type

        if event_type != "checkout.session.completed":
            raise EventIgnoreError()

        request_json = request.get_json(silent=True) or {}
        return Variables(variables={**request_json})
