## Stripe Trigger

**Author:** [bowenliang123](https://github.com/bowenliang123)

**Github Repository:** https://github.com/bowenliang123/dify-stripe-trigger

**Dify Marketplace:** https://marketplace.dify.ai/plugins/bowenliang123/stripe_trigger

### Stripe Trigger Plugin User Guide

#### What This Plugin Does
The Stripe Trigger plugin connects your Dify workflows with [Stripe Webhook events](https://docs.stripe.com/webhooks). When something happens in your Stripe workspace, like receiving an update for transaction, sessions and etc. , this trigger plugin automatically starts your Dify workflows to respond to these events.

### Available Events

Both types of Stripe webhook events are supported: Snapshot events and Thin events.

Stripe webhook events: 

- Snapshot events:    
  - The trigger plugin parse and check the signature of incoming Snapshot events.
  - Supported event types and payload structure of Snapshot Events: https://docs.stripe.com/api/events
  - The payload contains the full details of Strip events
  - Parameters to provide:
      - Singing secret for Webhooks
  
- Thin events (V2):
  - The trigger plugin parse and check the signature of incoming Thin Events notification, and retrieve the full event details from Stripe API.
  - Supported event types and payload structure of Thin Events: https://docs.stripe.com/api/v2/core/events
  - Parameters to provide:
    - Singing secret for Webhooks
    - API key
      - usually starts with "sk_" prefix
      - see more: https://docs.stripe.com/api/authentication
