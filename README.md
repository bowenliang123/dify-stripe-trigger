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
  - Strip docs for supported events and payload structure: https://docs.stripe.com/api/events
  - The payload contains the full details of Strip events
  - Parameters to provide:
      - Singing secret for Webhooks
  
- Thin events (V2): 
  - Strip docs for supported events and payload structure: https://docs.stripe.com/api/v2/core/events
  - This plugins helps to parse the thin events to get the full event from Stripe API.
  - Parameters to provide:
    - Singing secret for Webhooks
    - API key: commonly starts with "sk_" prefix
