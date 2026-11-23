# Composio Access Atlas — Independent AI Reviewer Assessment

**Date:** 23 November 2026. **Scope:** 100 apps × 6 fields = 600 records. **Reviewer:** AI assistant (not human). **Human-reviewed fields:** 0.

## Review methodology

All 600 supplied records were checked against source/evidence status, unknown values, disagreements and product identity flags. 25 targeted field decisions were separately supported by official documentation. The rest have not undergone full field-by-field independent web fact-checking; **do not use this as ground-truth accuracy**.

## Breakdown

| Review outcome | Fields |
|---|---:|
| UNVERIFIED_SOURCE_EXCERPT_MATCH | 260 |
| ONE_PASS_INSUFFICIENT | 112 |
| PARTIAL_AI_AGREEMENT | 62 |
| CONTRADICTORY_AI_PASSES | 38 |
| SOURCE_QUOTE_NOT_REPRODUCED | 37 |
| UNRESOLVED_VALUE | 23 |
| IDENTITY_RESEARCH_REQUIRED | 22 |
| SOURCE_CHECKED_CHANGE | 21 |
| MISSING_SOURCE | 21 |
| SOURCE_CHECKED_CONFIRMATION | 4 |

## Specific proposed corrections

- **Salesforce / auth_methods**: `(blank)` → `OAuth2`. Salesforce APIs document OAuth-based authentication. Source: https://developer.salesforce.com/docs/platform/api-rest/guide/intro-oauth-and-connected-apps.html
- **Salesforce / protocols**: `(blank)` → `REST; SOAP`. Salesforce REST and SOAP APIs are documented; ignore unsupported WebSocket/gRPC from second pass. Source: https://developer.salesforce.com/docs/atlas.en-us.integration_patterns_and_practices.meta/integ/integ_pat_selection_guide.htm
- **Zoho CRM / protocols**: `(blank)` → `REST`. Zoho CRM v8 documents a REST API. Source: https://www.zoho.com/crm/developer/docs/api/v8/request-methods.html
- **Zoho CRM / api_breadth**: `Unknown` → `Broad`. Official CRM API covers metadata, records, bulk, queries and other capabilities; qualitative breadth judgment. Source: https://www.zoho.com/crm/developer/docs/api/v8/
- **Zoho CRM / official_mcp**: `unknown` → `yes`. Zoho officially documents pre-built CRM MCP servers capable of CRM operations. Source: https://www.zoho.com/crm/developer/docs/mcp/overview.html
- **Freshdesk / auth_methods**: `API key` → `API key; Basic`. API key is used as username in HTTP Basic authentication (key:X). Source: https://developers.freshdesk.com/api/
- **Help Scout / auth_methods**: `Other` → `OAuth2`. Official Inbox API documents OAuth2; webhook-signature HMAC does not authenticate to its REST API. Source: https://developer.helpscout.com/mailbox-api/overview/authentication/
- **Help Scout / protocols**: `REST; WebSocket` → `REST`. Inbox API is HTTPS REST; webhooks are distinct from WebSocket. Source: https://developer.helpscout.com/mailbox-api/
- **Gladly / auth_methods**: `(blank)` → `Basic`. Gladly API explicitly specifies token-based HTTP Basic authentication. Source: https://developer.gladly.com/rest/
- **Zoho Cliq / auth_methods**: `(blank)` → `OAuth2`. Official Zoho Cliq API uses OAuth2. Source: https://www.zoho.com/cliq/help/restapi/v3/introduction/
- **Zoho Cliq / protocols**: `(blank)` → `REST`. Official Zoho Cliq v3 documentation describes REST API. Source: https://www.zoho.com/cliq/help/restapi/v3/introduction/
- **Zoho Cliq / official_mcp**: `unknown` → `yes`. Zoho documents its own MCP server with Cliq tools. Source: https://www.zoho.com/cliq/help/platform/configure-zoho-cliq-mcp.html
- **Google Ads / protocols**: `REST; WebSocket; gRPC` → `REST; gRPC`. Google Ads API supports REST and gRPC transports. WebSocket in supplied final value is unsupported. Source: https://developers.google.com/google-ads/api/docs/concepts/call-structure
- **Mailchimp / official_mcp**: `no` → `yes`. Official Marketing MCP indexes documentation, not merchant account actions; distinguish transactional MCP. Source: https://mailchimp.com/developer/marketing/build/ai-tools/mcp-server
- **Airtable / protocols**: `CLI/library; REST; WebSocket` → `CLI/library; REST`. Airtable web API is RESTful; an SDK is available, but WebSocket was not established. Source: https://airtable.com/developers/web/api/introduction
- **Jira / auth_methods**: `Bearer/PAT` → `Basic; Bearer/PAT; OAuth2`. Jira Cloud REST supports OAuth2 and Basic using email + API token; exact bearer/PAT taxonomy requires nuance. Source: https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/
- **Jira / protocols**: `CLI/library` → `CLI/library; REST`. Jira Cloud REST v3 exists; Forge CLI is an additional tooling surface. Source: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- **Jira / api_breadth**: `Unknown` → `Broad`. Jira REST v3 exposes extensive resources and operations; breadth is analyst judgment. Source: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- **Monday.com / protocols**: `GraphQL; REST` → `GraphQL`. monday.com core platform API is GraphQL, not a standard REST resources API; do not count transport over HTTP as REST. Source: https://developer.monday.com/api-reference/docs/introduction-to-graphql
- **QuickBooks / access_tier**: `unknown` → `free_self_serve`. Developer account, app registration, and sandbox instructions are self-service; distinguish production/account access from sandbox. Source: https://developer.intuit.com/app/developer/qbo/docs/
- **QuickBooks / protocols**: `(blank)` → `REST`. QuickBooks Online accounting API has a documented REST interface. The broader Intuit documentation also references GraphQL; REST is the minimum confirmed interface. Source: https://developer.intuit.com/app/developer/qbo/docs/

## Important caveats

- **Paygent Connect — PRODUCT IDENTITY:** Current 6 fields use NMI docs; several similarly named Paygent products exist. No evidence confirms this is the assigned product. Treat final values as unresolved until identity established. [https://www.gopaygent.com/](https://www.gopaygent.com/)
- **NotebookLM — PRODUCT SCOPE:** NotebookLM Enterprise API requires enterprise licensing. Do not attribute the same API to consumer NotebookLM without verified docs. [https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks](https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks)
- **Google Ads — PRODUCTION ACCESS:** Developer/test access and production account authorization differ; verify current access requirements; note Google Ads docs reflect newer developer-token policies. [https://developers.google.com/google-ads/api/docs/get-started/introduction](https://developers.google.com/google-ads/api/docs/get-started/introduction)
- **WhatsApp Business — APP REVIEW:** App review and permissions may apply to distributed solution-provider integrations, independently from test access. [https://developers.facebook.com/docs/whatsapp/solution-providers/app-review/sample-submission](https://developers.facebook.com/docs/whatsapp/solution-providers/app-review/sample-submission)
- **WooCommerce — MCP VERSION:** Official MCP exists in developer preview but now needs WordPress MCP Adapter, not old WooCommerce-specific endpoint. [https://developer.woocommerce.com/docs/features/mcp/](https://developer.woocommerce.com/docs/features/mcp/)
- **MrScraper — MULTIPLE AUTH SURFACES:** REST x-api-token vs proxy basic vs MCP OAuth. Do not pool them as a single endpoint authentication policy. [https://docs.mrscraper.com/docs/api/overview](https://docs.mrscraper.com/docs/api/overview)
- **Help Scout — SOURCE ROLE:** Webhook signature is not API authentication; community MCP is not official vendor MCP. [https://developer.helpscout.com/mailbox-api/overview/authentication/](https://developer.helpscout.com/mailbox-api/overview/authentication/)
- **Mailchimp — MCP TYPE:** Official marketing documentation MCP does not mean account-data actions; distinguish separate transactional MCP. [https://mailchimp.com/developer/marketing/build/ai-tools/mcp-server](https://mailchimp.com/developer/marketing/build/ai-tools/mcp-server)
- **QuickBooks — API SURFACE:** The complete QuickBooks Online developer documentation covers OAuth2 and a REST accounting API; earlier blank protocols are incorrect. [https://developer.intuit.com/app/developer/qbo/docs/](https://developer.intuit.com/app/developer/qbo/docs/)
- **monday.com — API SURFACE:** Platform API is GraphQL. Additional platform AI gateway HTTP endpoints should not be mixed into the general CRUD API protocol classification. [https://developer.monday.com/api-reference/docs/introduction-to-graphql](https://developer.monday.com/api-reference/docs/introduction-to-graphql)

Human audit remains pending. Do not autofill names, dates or truth fields, and do not claim the full 600 are fact-checked. Apply verified corrections only to final dataset, retaining original model predictions and the full evaluation provenance.
