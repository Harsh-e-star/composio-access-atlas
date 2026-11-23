"""Reproducible seeded dataset. Doc-reviewed annotations come from directly inspected official docs.
Unreviewed apps deliberately remain unknown rather than guesses disguised as findings.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATEGORIES={
'CRM & Sales': '''Salesforce|salesforce.com|Enterprise CRM and sales automation
HubSpot|hubspot.com|CRM, marketing, and customer data
Pipedrive|pipedrive.com|Pipeline and deal management
Attio|attio.com|Customizable collaborative CRM
Twenty|twenty.com|Open-source relationship management CRM
Podio|podio.com|Custom workspaces and CRM workflows
Zoho CRM|zoho.com/crm|Sales CRM and automation
Close|close.com|Sales CRM for outbound teams
Copper|copper.com|Google Workspace-focused CRM
DealCloud|api.docs.dealcloud.com|Deal and relationship management for finance''',
'Support & Helpdesk': '''Zendesk|zendesk.com|Customer support tickets and service
Intercom|intercom.com|Customer messaging and support platform
Freshdesk|freshdesk.com|Omnichannel support ticketing
Front|front.com|Collaborative customer inbox and support
Pylon|usepylon.com|B2B customer support workspace
LiveAgent|liveagent.com|Multichannel help desk software
Plain|plain.com|API-first B2B support
Help Scout|helpscout.com|Shared inbox and customer help desk
Gorgias|gorgias.com|Ecommerce customer support
Gladly|gladly.com|Person-centric customer service''',
'Communications': '''Slack|slack.com|Workspace messaging and automation
Twilio|twilio.com|Programmable messages, calls and communications
Zoho Cliq|zoho.com/cliq|Team messaging and collaboration
Lark (Larksuite)|open.larksuite.com|Team productivity and messaging
Pumble|pumble.com|Workplace messaging platform
Discord|discord.com|Community chat, bots and voice
Telegram|core.telegram.org|Messaging platform with Bot API
WhatsApp Business|developers.facebook.com/docs/whatsapp|Business messaging via Meta cloud APIs
Aircall|aircall.io|Cloud phone system for sales/support
Vonage|developer.vonage.com|Programmable communication APIs''',
'Marketing & Social': '''Google Ads|developers.google.com/google-ads|Search and display advertising platform
Meta Ads|developers.facebook.com/docs/marketing-apis|Advertising across Meta properties
LinkedIn Ads|learn.microsoft.com/linkedin/marketing|B2B marketing and ad campaigns
GoHighLevel|highlevel.stoplight.io|Agency CRM and marketing funnels
Mailchimp|mailchimp.com/developer|Email marketing and audiences
Klaviyo|developers.klaviyo.com|Marketing automation and customer data
systeme.io|systeme.io|Funnels, campaigns and course sales
Pinterest|developers.pinterest.com|Visual discovery and ads
Threads (Meta)|developers.facebook.com/docs/threads|Social posts and engagement
SendGrid|sendgrid.com|Transactional and marketing email''',
'Ecommerce': '''Shopify|shopify.dev|Online stores and merchant operations
WooCommerce|woocommerce.com/document/woocommerce-rest-api|WordPress store commerce APIs
BigCommerce|developer.bigcommerce.com|SaaS commerce storefront platform
Salesforce Commerce Cloud|developer.salesforce.com/docs/commerce|Enterprise digital commerce
Magento (Adobe Commerce)|developer.adobe.com/commerce|Self-hosted and enterprise commerce
Squarespace|developers.squarespace.com|Website builder with commerce features
Ecwid|api-docs.ecwid.com|Embeddable ecommerce storefronts
Gumroad|gumroad.com/api|Digital product commerce
Amazon Selling Partner|developer-docs.amazon.com/sp-api|Marketplace seller inventory and orders
fanbasis|fanbasis.com|Creator commerce and monetization''',
'Data, SEO & Scraping': '''DataForSEO|docs.dataforseo.com|Search and SEO data APIs
SE Ranking|seranking.com/api|SEO monitoring and rank tracking
Ahrefs|ahrefs.com/api|Search analytics and backlink intelligence
MrScraper|docs.mrscraper.com|Web extraction and scraping service
Apify|docs.apify.com|Cloud scraping actors and automation
Firecrawl|firecrawl.dev|Web crawling, extraction and search APIs
Bright Data|brightdata.com|Web data collection and proxy services
Sherlock|github.com/sherlock-project/sherlock|Open-source username OSINT CLI
Waterfall.io|waterfall.io|Contact and company intelligence
Clay|clay.com|Prospecting and data-enrichment workflows''',
'Developer & Infrastructure': '''GitHub|docs.github.com/rest|Code hosting and developer collaboration
Vercel|vercel.com/docs/rest-api|Frontend deployments and hosting
Netlify|docs.netlify.com/api|Web deployment and hosting automation
Cloudflare|developers.cloudflare.com/api|Edge network and security services
Supabase|supabase.com/docs|Postgres backend and auth platform
Neo4j|neo4j.com/docs/api|Graph database platform
Snowflake|docs.snowflake.com|Cloud analytics data warehouse
MongoDB Atlas|mongodb.com/docs/atlas/api|Managed document databases
Datadog|docs.datadoghq.com/api|Infrastructure monitoring and observability
Sentry|docs.sentry.io/api|Application error and performance monitoring''',
'Productivity & Projects': '''Notion|developers.notion.com|Documents, databases and knowledge work
Airtable|airtable.com/developers|Low-code databases and workflows
Linear|linear.app/developers|Product issue tracking and roadmaps
Jira|developer.atlassian.com|Issue tracking and agile development
Asana|developers.asana.com|Tasks and team project planning
Monday.com|developer.monday.com|Work operating system and boards
ClickUp|clickup.com/api|Tasks, docs and project management
Coda|coda.io/developers|Docs, tables and automations
Smartsheet|smartsheet.com/developers|Enterprise work collaboration
Harvest|help.getharvest.com/api-v2|Time tracking, project budgets and invoicing''',
'Finance & Fintech': '''Stripe|stripe.com/docs/api|Payments, billing and revenue infrastructure
Plaid|plaid.com/docs|Financial account data connectivity
Binance|binance-docs.github.io|Crypto exchange and trading APIs
Paygent Connect|paygent.com|Payment gateway connectivity
ipayx|ipayx.ai/docs|Payment processing API platform
QuickBooks|developer.intuit.com|Small business accounting software
Xero|developer.xero.com|Small business cloud accounting
Brex|developer.brex.com|Business cards and spend management
Ramp|docs.ramp.com|Corporate spend and expense platform
PitchBook|pitchbook.com|Private company and investment intelligence''',
'AI, Research & Media': '''NotebookLM|cloud.google.com/gemini|AI notebook and source-grounded research
Otter AI|help.otter.ai|Meeting transcription and notes
Fathom|fathom.video|AI meeting notes and summaries
Consensus|consensus.app|Academic evidence search
Reducto|reducto.ai|Document parsing and extraction
Devin|docs.devin.ai|AI software engineering assistant
higgsfield|higgsfield.ai/cli|Generative video and image content suite
Mermaid CLI|github.com/mermaid-js/mermaid-cli|CLI rendering of Mermaid diagrams
YouTube Transcript|transcriptapi.com|Video transcript extraction APIs
Grain|grain.com|Meeting recording and conversation insights'''
}

# Official documentation examined Nov 23 2026. Fields not independently supported must say unknown.
# Format: name -> [auth, access, surface, mcp, blocker, evidence-url, insight]
V={
'Salesforce':['OAuth2','Conditional','REST','Unknown','Connected-app setup; tenant permissions','https://developer.salesforce.com/docs/platform/api-rest/guide/intro-oauth-and-connected-apps.html','REST resources require an external client app or connected app.'],
'HubSpot':['OAuth2 + service key','Conditional','REST','Unknown','Account app setup; legacy private app sunset','https://developers.hubspot.com/changelog/legacy-private-app-creation-sunset','New accounts use service keys for in-account API integrations; OAuth for public apps.'],
'Pipedrive':['OAuth2 + API token','Conditional','REST','Unknown','Needs tenant account/token','https://pipedrive.readme.io/docs/core-api-concepts-authentication','Marketplace apps use OAuth; personal integrations can use API tokens.'],
'Attio':['API key','Conditional','REST','Unknown','Workspace scope and permissions','https://attio.com/help/reference/apps/generating-an-api-key','Keys can be generated from an Attio workspace.'],
'Twenty':['API key','Self-serve','REST + GraphQL','Unknown','User must run cloud or self-hosted workspace','https://github.com/twentyhq/twenty/blob/main/packages/twenty-docs/developers/extend/api.mdx','Core APIs include workspace REST and GraphQL.'],
'Zendesk':['OAuth2 + legacy API token','Conditional','REST','Unknown','OAuth migration and tenant consent','https://developer.zendesk.com/documentation/authentication/oauth-migration/','Support API tokens are being retired in phases through April 2027.'],
'Intercom':['OAuth2 + access token','Conditional','REST','Unknown','Paid workspace for private-app tokens','https://developers.intercom.com/docs/build-an-integration/learn-more/authentication/setting-up-oauth','Public apps use OAuth; private apps use workspace tokens.'],
'Front':['OAuth2 + API token','Conditional','REST','Unknown','Partners generally must use OAuth','https://dev.frontapp.com/me/docs/create-and-revoke-api-tokens','Partners must implement OAuth unless an exception is granted.'],
'Slack':['OAuth2 + bot/user token','Self-serve','REST','Unknown','App scopes and workspace installation','https://docs.slack.dev/apis/web-api/','Web API supports bot/user bearer tokens obtained through OAuth.'],
'Twilio':['HTTP Basic + API key','Self-serve','REST','Unknown','Project credentials and account limits','https://www.twilio.com/docs/iam/credentials/api','API key+secret pairs authenticate via HTTP Basic.'],
'Discord':['OAuth2 + bot token','Self-serve','REST','Unknown','Bot permissions; self-bot automation prohibited','https://github.com/discord/discord-api-docs/blob/main/developers/reference.mdx','Official API documents bot and OAuth access tokens.'],
'Telegram':['Bot token','Self-serve','Bot HTTP API','Unknown','Bot-only privileges; no user impersonation','https://core.telegram.org/bots/api','Bot API is an HTTP interface using bot tokens.'],
'WhatsApp Business':['Bearer token','Conditional','Graph API','Unknown','Business onboarding; production messaging restrictions','https://developers.facebook.com/documentation/business-messaging/whatsapp/overview/','Cloud API uses bearer access tokens; production may require business setup.'],
'Google Ads':['OAuth2 + developer token','Conditional','REST + gRPC','Unknown','Developer token access tier/application review','https://developers.google.com/google-ads/api/docs/oauth/overview','Both OAuth and a Google Ads developer token are required.'],
'LinkedIn Ads':['OAuth2','Gated','REST','Unknown','Permission/product access approval','https://learn.microsoft.com/en-us/linkedin/marketing/increasing-access?view=li-lms-2026-10','Advertising and restricted products have tiered approval paths.'],
'Pinterest':['OAuth2','Conditional','REST','Unknown','Trial-access application approval','https://developers.pinterest.com/docs/getting-started/connect-app/','Product-limited test tokens require approved trial access.'],
'Shopify':['OAuth2 + access token','Conditional','GraphQL','Unknown','App installation and merchant scopes','https://shopify.dev/docs/api/usage/authentication','GraphQL Admin API uses merchant-scoped access tokens.'],
'Magento (Adobe Commerce)':['Token + OAuth1 / OAuth2','Conditional','REST + GraphQL','Unknown','Edition-dependent auth; admin role','https://developer.adobe.com/commerce/webapi/get-started/authentication/','Open Source/Commerce and Commerce Cloud Service differ in auth.'],
'Amazon Selling Partner':['OAuth2 (LWA)','Gated','REST','Unknown','Seller/vendor registration, role approval','https://developer-docs.amazon.com/sp-api/docs/sp-api-registration-overview','SP-API requires developer registration; private app may require professional seller account.'],
'Sherlock':['No service auth','Self-serve','Local CLI','No','Not a hosted API; wrap CLI as local skill','https://github.com/sherlock-project/sherlock','Open-source OSINT command-line project, not a remote authenticated SaaS API.'],
'DataForSEO':['HTTP Basic','Conditional','REST','Unknown','Developer account and usage billing','https://docs.dataforseo.com/v3/auth/','API v3 explicitly requires HTTP Basic auth.'],
'Ahrefs':['API key','Paid','REST','Yes','Eligible subscription and API unit quota','https://docs.ahrefs.com/en/api/docs/introduction','API availability depends on eligible paid plans; MCP also exists.'],
'Apify':['API token','Self-serve','REST + MCP','Yes','Actors have usage quotas','https://docs.apify.com/agents/quickstart','Account API token and MCP-supported agent workflows documented.'],
'Firecrawl':['API key','Self-serve','REST + MCP','Yes','Usage quotas, website restrictions','https://github.com/firecrawl/firecrawl-mcp-server','Official MCP server and hosted MCP endpoint documented.'],
'GitHub':['PAT + GitHub App + OAuth','Self-serve','REST','Yes','Permission scope and org approval on some repos','https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api','PAT, GitHub App and OAuth tokens are documented.'],
'Vercel':['Bearer token','Self-serve','REST','Unknown','Team access and token scopes','https://vercel.com/docs/rest-api','REST endpoints use bearer tokens.'],
'Cloudflare':['API token','Self-serve','REST','Unknown','Token permissions and account ownership','https://developers.cloudflare.com/api/overview/','Granular API tokens can be generated in the dashboard.'],
'Sentry':['Bearer token','Self-serve','REST','Unknown','Organization/issue permissions','https://docs.sentry.io/api/auth/','API supports bearer auth tokens.'],
'Airtable':['PAT + OAuth2','Self-serve','REST','Unknown','Token scopes, resource and workspace permissions','https://support.airtable.com/articles/9934989703-creating-personal-access-tokens','Personal access tokens replace legacy keys; OAuth for third parties.'],
'Linear':['PAT + OAuth2','Self-serve','GraphQL','Unknown','Workspace permissions and rate limits','https://linear.app/developers/graphql','GraphQL API supports personal keys and OAuth2.'],
'Jira':['OAuth2 + API token','Conditional','REST','Unknown','Atlassian app scopes or site/admin consent','https://developer.atlassian.com/cloud/jira/platform/security-overview/','OAuth 3LO and API-token Basic auth supported.'],
'Stripe':['Secret API key','Self-serve','REST','Unknown','Real payments require account activation','https://docs.stripe.com/api','API reference uses secret keys; test mode exists.'],
'Plaid':['Client ID + secret','Self-serve','REST','Unknown','Production approval/onboarding; sandbox easy','https://plaid.com/docs/api/','Almost all endpoints require client_id and secret; sandbox available.'],
'QuickBooks':['OAuth2','Self-serve','REST + GraphQL','Yes','Company authorization; hosted MCP pilot is invite-only','https://developer.intuit.com/app/developer/qbo/docs/','Developer portal registers OAuth2 apps; accounting API docs.'],
'Xero':['OAuth2','Self-serve','REST','Yes','Org consent and rate limits; paid connection rules possible','https://developer.xero.com/documentation/getting-started-guide/','Free Xero developer registration and OAuth app setup.'],
'Ramp':['OAuth2','Conditional','REST','Unknown','Business account/scoped developer app','https://docs.ramp.com/developer-api/v1/authorization','Client ID/secret used for OAuth2 token flow.'],
'Reducto':['API key','Paid','REST + MCP','Yes','Usage billing / credits','https://reducto.ai/developers','API, OpenAPI specification, CLI and MCP server documented.'],
'Mermaid CLI':['No service auth','Self-serve','Local CLI','No','Not a remote API; use sandboxed local skill','https://github.com/mermaid-js/mermaid-cli','CLI transforms diagram definitions into SVG, PNG or PDF.'],
'NotebookLM':['Google IAM / OAuth','Gated','REST (Enterprise)','Unknown','Requires active enterprise license and project IAM','https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks','Notebook Enterprise REST methods require an active license.'],
'Otter AI':['MCP auth (check plan)','Conditional','MCP','Yes','MCP client/account setup; API breadth unconfirmed','https://help.otter.ai/hc/en-us/articles/35287607569687-Otter-MCP-Server','First-party MCP server documented; REST surface not established.'],
'Consensus':['API key + MCP OAuth','Conditional','REST + MCP','Yes','Paid usage allowances / quota','https://help.consensus.app/en/articles/16516328-the-consensus-api','API and MCP dashboard supports issuing API keys; plan-linked calls.'],
}

# Additional official docs to clarify special cases / MCP state.
EXTRA={
'Ahrefs':['https://help.ahrefs.com/en/articles/13913559-getting-started-with-ahrefs-mcp'],
'Google Ads':['https://developers.google.com/google-ads/api/docs/api-policy/access-levels'],
'LinkedIn Ads':['https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access'],
'Amazon Selling Partner':['https://developer-docs.amazon.com/sp-api/docs/onboarding-overview'],
'Zendesk':['https://support.zendesk.com/hc/en-us/articles/10851263566234-Announcing-the-removal-of-API-tokens-as-an-authentication-method-for-API-requests'],
'QuickBooks':['https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0'],
'Xero':['https://developer.xero.com/faq','https://developer.xero.com/documentation/guides/remote-mcp/overview'],
'QuickBooks':['https://help.developer.intuit.com/s/question/0D5TR00001ahNXF0A2/how-can-a-buildertier-developer-join-the-intuit-ai-pilot-hosted-mcp-and-are-bankfeed-tools-for-review-categorizing-matching-transfers-available-or-planned'],
'GitHub':['https://github.com/github/github-mcp-server'],
'Notion':['https://developers.notion.com/docs/authorization'],
'Firecrawl':['https://github.com/firecrawl/firecrawl-mcp-server/blob/main/server.json'],
}

out=[]
for cat,block in CATEGORIES.items():
    for line in block.splitlines():
        name,hint,description=line.split('|')
        item={'id':len(out)+1,'app':name,'category':cat,'summary':description,
              'hint':'https://'+hint,'auth':'Unknown','access':'Unknown','surface':'Unknown',
              'mcp':'Unknown','blocker':'Needs source verification','review':'Needs research',
              'evidence':[],'note':'Queued for automated research and human spot-check.'}
        if name in V:
            auth,access,surface,mcp,blocker,evidence,note=V[name]
            item.update(auth=auth,access=access,surface=surface,mcp=mcp,blocker=blocker,
                        review='Docs reviewed',evidence=[evidence]+EXTRA.get(name,[]),note=note)
        out.append(item)
assert len(out)==100, len(out)
assert len({r['app'] for r in out})==100
assert len(V)==sum(r['review']=='Docs reviewed' for r in out)
(ROOT/'data'/'apps.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf8')
print(f'Wrote {len(out)} apps; {len(V)} source-reviewed, {100-len(V)} research-queued')
