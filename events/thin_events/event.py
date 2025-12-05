from collections.abc import Mapping
from typing import Any

from dify_plugin.entities.trigger import Variables
from dify_plugin.errors.trigger import EventIgnoreError
from dify_plugin.interfaces.trigger import Event
from werkzeug import Request


class StripeThinEvents(Event):
    """
    Doc of thin events:
    https://docs.stripe.com/api/v2/core/events
    """

    def _on_event(self, request: Request, parameters: Mapping[str, Any], payload: Mapping[str, Any]) -> Variables:
        stripe_event: dict[str, Any] = payload.get("stripe_event")
        if not stripe_event:
            raise EventIgnoreError("stripe_event is empty")

        request_json = request.get_json(silent=True) or {}
        return Variables(variables={**request_json})
