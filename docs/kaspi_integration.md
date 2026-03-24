# Kaspi API Integration Checklist

We will wire the live adapter as soon as official API details are available.

## Required from Kaspi / Partner Cabinet
- API base URL
- Auth method (token / OAuth / HMAC)
- How to list offers (SKU, title, NTIN, price, availability)
- How to update prices (single/bulk endpoints, limits)
- Rate limits and polling guidance
- Sandbox or test store credentials

## Adapter mapping (expected fields)
- sku (string)
- title (string)
- ntin (string, optional)
- price (number)
- currency (KZT)
- available (bool)
- updated_at (datetime)

## Open questions
- How to fetch competitor prices / positions (if allowed)
- Whether offer list includes NTIN
- Bulk update constraints (batch size, cooldown)
