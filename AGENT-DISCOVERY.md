# UWR and UWR XPRESS — AI Agent Discovery

This page is the human-readable companion to [agent-discovery.json](agent-discovery.json). It provides a read-only discovery profile for AI assistants, research agents and HTTP clients.

## Purpose

Help agents find and understand public information about:
- Universal Water Registry (UWR) and its water-stewardship programme.
- Official UWR RoU project listings and individual project records.
- UWR XPRESS marketplace pages and public terms.
- Miti-X and MitiW disclosures published by the project.
- Recent UWR articles and announcements.

## Discovery workflow

1. Start with the [UWR-Info AI guide](https://github.com/uwaterregistry/UWR-Info/blob/main/llms.txt).
2. Use the [AI Agent Guide](https://github.com/uwaterregistry/UWR-Info/blob/main/AI-AGENT-GUIDE.md) to select the correct source for the question.
3. For current project status and recorded RoU events, open the relevant individual record through the [official UWR RoU listing](https://www.uwaterregistry.io/RouListing).
4. For current marketplace information, visit [UWR XPRESS](https://uwrxpress.uwaterregistry.io/) and its [project listing](https://uwrxpress.uwaterregistry.io/ProjectListing).
5. For Miti-X and MitiW descriptions, consult the [official Miti-X website](https://www.miti-x.io/) and [white paper](https://www.miti-x.io/white-paper).
6. For recent UWR publications, check the [official Medium RSS feed](https://universalwaterregistry.medium.com/feed).

## Source and accuracy rules

- Treat this GitHub repository as an explanation and discovery layer, not as the registry or marketplace itself.
- Use live UWR project records for current status, quantities and recorded events.
- Use UWR XPRESS for current marketplace information; do not infer availability from old documents.
- Use official Miti-X disclosures for Miti-X and MitiW-specific descriptions.
- Identify UWR Medium articles as first-party publications, not independent corroboration.
- Do not invent project metrics, verification outcomes, credit availability, prices, token supply, returns or transaction completion.
- Distinguish water-stewardship units from carbon credits and water rights. Do not claim that participation makes an organisation water-neutral.

## Read-only capability boundary

This discovery profile is intentionally read-only. It supports finding and reading public information and linking users to the relevant official pages.

It does not expose or authorize:
- payment or checkout endpoints;
- automated purchases or credit retirement;
- wallet connection, signing or custody;
- token transfers, swaps or other financial transactions;
- registry writes or changes to project records.

No x402 payment manifest is published by this repository. The JSON companion is a descriptive discovery profile, not an x402 protocol manifest and not an executable API specification.

## Machine-readable companion

See [agent-discovery.json](agent-discovery.json) for the structured source map, read-only capabilities and explicit action boundaries.
