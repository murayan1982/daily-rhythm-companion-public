# DRC v4.1.0 GP-0 Backend / Privacy Decision Control

## Control metadata

| Field | Value |
| --- | --- |
| Task ID | `DRC_V410_GP0_BACKEND_PRIVACY_DECISION_CONTROL_CORRECTIVE_R1` |
| Baseline commit | `45d6a543165321e30757808095a545b0d9bc9ec1` |
| Development line | DRC v4.1.0 |
| Primary target | Google Play |
| GP0-D03 status | `NOT_DECIDED` |
| GP0-D08 status | `NOT_DECIDED` |
| Product source implementation | `NOT_AUTHORIZED` |
| Backend wiring | `NOT_AUTHORIZED` |
| Decision owner | User |
| Implementation/research support | Codex |
| Evidence access date | 2026-09-19 |

This control organizes evidence and unanswered choices. It does not implement a network, product, Backend, hosting, privacy, or publication change.

## Non-decision boundary

Codex does not automatically choose or approve: hosting/cloud provider; production domain; deployment region; data controller/operator identity; support/privacy contact; data retention period; deletion completion period; third-party processor; health-data provider; LLM provider; service pricing commitment; publication country/region; or any legal conclusion. Every unanswered field remains `NOT_DECIDED`. Candidate classes are vocabulary, not recommendations or approvals.

## Current-state evidence inventory

### Source-confirmed facts

| Area | Current evidence | Source anchor |
| --- | --- | --- |
| Backend default | `DRC_BACKEND_API_BASE_URL` defaults to `http://127.0.0.1:8000`; localhost detection is explicit. | `app/lib/services/backend_api_client.dart:25-36` |
| Production Backend | Architecture says it remains unwired pending GP0-D03/D08; production operations are symbolic dispositions, not a network client. | `docs/v410_gp2_production_boundary_architecture.md:113`; `app/lib/production/backend/production_backend_operation.dart:1-80` |
| Production exclusions | Voice, realtime, motion, demo, developer/operator controls, raw diagnostics, and lifecycle controls are outside the production capability boundary. | `docs/v410_gp2_text_core_capability_boundary.md:11-38`; `app/lib/production/core/production_capability.dart` |
| Route surface | FastAPI assembles health, character, sleep/provider, daily-record, advice, chat, Fitbit, Google Health, demo, realtime, voice, and motion routers. | `backend/app/main.py:1-61` |
| Sleep summary | Flutter reads `GET /sleep/summary` into `SleepSummary`. | `app/lib/services/backend_api_client.dart:98-110` |
| Health/provider metadata | Flutter reads provider selection plus Fitbit/Google Health connection/status/diagnostic metadata. | `app/lib/services/backend_api_client.dart:112-127,232-328` |
| Mood | Mood is sent with character and sleep context in advice requests. | `app/lib/services/backend_api_client.dart:521-538` |
| Character | Flutter reads `/characters`; selected character data enters advice/chat context. | `app/lib/services/backend_api_client.dart:83-95,441-465,521-538` |
| Advice | Flutter posts character, sleep, and mood to `/advice`. | `app/lib/services/backend_api_client.dart:521-541` |
| Optional text chat | Flutter creates `/chat/sessions` and posts session messages. | `app/lib/services/backend_api_client.dart:441-519` |
| History | Flutter reads daily records, trends, weekly summaries, and rhythm reports. | `app/lib/services/backend_api_client.dart:129-229` |
| Storage | Local daily-record and OAuth-token stores exist; the token store writes JSON under Backend `local_data`. These are not approved production stores. | `backend/app/services/daily_record_store.py` (`DailyRecordStore`); `backend/app/services/google_health_token_store.py:85-149,190-192` |
| Deletion | Voice staging/output stores have bounded count/size/TTL cleanup and remove rejected/expired artifacts; these are demo/development behaviors. | `backend/app/services/voice_input_staging_store.py:50-197`; `backend/app/services/voice_output_artifact_store.py:36-215` |
| Logging | Diagnostic/status paths exist, but no production logging, monitoring, redaction, retention, or access policy is accepted. | `backend/app`; `docs/v410_gp2_text_core_capability_boundary.md:96-131` |
| Authentication/account | Current `BackendApiClient` calls do not attach an app-user authorization credential; no production account lifecycle is established. | `app/lib/services/backend_api_client.dart` (`BackendApiClient`) |
| Secrets/configuration | Environment/config and local OAuth stores exist; no production secret store, owner, injection, or rotation contract is approved. | `backend/app/config.py`; `backend/app/services/google_health_token_store.py` |

### Inferences requiring decision or later verification

- A reachable HTTPS service is likely required if approved product operations use the Backend, but provider, URL, region, ownership, and price are not implied.
- Local stores/cleanup are not proof of production retention, deletion, backup, encryption, residency, or recovery guarantees.
- Missing app-user authorization headers indicate an authentication decision is needed; anonymous production access is not approved.
- Data categories may require different purpose, retention, deletion, and disclosure choices; this control makes no legal classification.
- Production boundaries exclude non-product capabilities conceptually; artifact exclusion and deployed route exposure still require later evidence.

## GP0-D03 decision matrix

All rows and approved values remain `NOT_DECIDED`.

| Decision item | Current evidence | Required choice | Allowed values / candidate classes | Dependency | Owner | Status | Approved value | Evidence required |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| production Backend hosting model | Local FastAPI only | Select operating model | PaaS / serverless / container / VM / other / no remote Backend | GP-2/4 | User | NOT_DECIDED | NOT_DECIDED | Architecture/account/contract evidence |
| hosting/provider ownership | No owner | Name account owner/admins | Individual / organization / delegate / other | Hosting | User | NOT_DECIDED | NOT_DECIDED | Account roles |
| production base URL | Localhost default | Approve URL source/value | Custom HTTPS / provider HTTPS / none | GP-4 | User | NOT_DECIDED | NOT_DECIDED | DNS/TLS/artifact evidence |
| custom domain ownership | None recorded | Choose domain model/owner | Existing / new / provider / none | URL | User | NOT_DECIDED | NOT_DECIDED | Ownership/renewal evidence |
| HTTPS/TLS termination | Local HTTP | Choose termination/cert owner | Provider / load balancer / proxy / other | Domain | User | NOT_DECIDED | NOT_DECIDED | TLS/renewal evidence |
| deployment region | None approved | Choose region(s) | Single / multi / provider default / other | D08 | User | NOT_DECIDED | NOT_DECIDED | Deployment evidence |
| data residency | Local stores | Define allowed location by category | Region / multi-region / no persistence / other | D08 | User | NOT_DECIDED | NOT_DECIDED | Flow/storage evidence |
| app-to-Backend authentication | No user auth header | Choose auth boundary | Anonymous bounded / attestation / user token / gateway / other | Account | User | NOT_DECIDED | NOT_DECIDED | Threat model/requests |
| abuse/rate-limit protection | None accepted | Select controls | WAF / gateway / app / combined | Exposure | User | NOT_DECIDED | NOT_DECIDED | Limits/alerts/tests |
| secret storage/rotation owner | Dev config/stores | Select store/custodian | Secret manager / vault / other | Hosting | User | NOT_DECIDED | NOT_DECIDED | Access/rotation/recovery |
| logging/monitoring | No policy | Define metrics/logs/alerts | Provider / external / self-hosted / minimal | D08 | User | NOT_DECIDED | NOT_DECIDED | Schema/redaction/retention |
| backup/recovery | No contract | Define backup/restore | None / provider / custom / other | Storage | User | NOT_DECIDED | NOT_DECIDED | Restore test |
| deployment/rollback owner | None | Assign authority/process | User / org role / delegate / other | Hosting | User | NOT_DECIDED | NOT_DECIDED | Runbook/roles |
| incident response owner | None | Assign response owner | User / team / delegate / other | Monitoring | User | NOT_DECIDED | NOT_DECIDED | Runbook/contact |
| availability target | None | Choose target/posture | Best effort / SLO / scheduled / other | Cost | User | NOT_DECIDED | NOT_DECIDED | SLO measurement |
| operating-cost ceiling | None | Set budget/overage action | Monthly / usage / alerts / other | Provider | User | NOT_DECIDED | NOT_DECIDED | Pricing/budget owner |
| CORS/network exposure | Broad Backend routes | Define clients/origins/ingress/routes | Gateway / restricted origins / public bounded / private / other | Auth/GP-2 | User | NOT_DECIDED | NOT_DECIDED | Network/route tests |
| environment separation | No contract | Define dev/stage/prod isolation | Accounts/projects / services / config / other | Secrets | User | NOT_DECIDED | NOT_DECIDED | Isolation evidence |
| localhost removal acceptance evidence | Release default is localhost | Choose proof | Static scan / runtime trace / both / other | GP-4/6 | User | NOT_DECIDED | NOT_DECIDED | AAB config/scan/trace |

## GP0-D08 decision matrix

All rows and approved values remain `NOT_DECIDED`.

| Decision item | Current evidence | Required choice | Allowed values / candidate classes | Dependency | Owner | Status | Approved value | Evidence required |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| data controller/operator identity | None approved | Name accountable operator | Individual / organization / other | Ownership | User | NOT_DECIDED | NOT_DECIDED | Identity evidence |
| privacy contact | None | Select public channel | Email / form / postal / combined | Operator | User | NOT_DECIDED | NOT_DECIDED | Controlled contact |
| support contact | None | Select support channel | Email / form / store / combined | Operations | User | NOT_DECIDED | NOT_DECIDED | Monitored contact |
| collected data categories | Multiple candidates | Approve field inventory | Collected / not / ephemeral by category | Product | User | NOT_DECIDED | NOT_DECIDED | Runtime/network inventory |
| required versus optional data | Not approved | Classify each category | Required / optional / conditional / not collected | UX | User | NOT_DECIDED | NOT_DECIDED | UX/failure evidence |
| on-device versus off-device processing | Backend calls exist | Choose location | Device / DRC Backend / third party / mixed | D03 | User | NOT_DECIDED | NOT_DECIDED | Data-flow trace |
| purposes of processing | Product/diagnostic flows | Approve each purpose | Core / security / support / analytics / other | Inventory | User | NOT_DECIDED | NOT_DECIDED | Field-purpose map |
| health/sleep data handling | Routes exist | Define lifecycle | Device / ephemeral / retained / processor / other | Provider/D03 | User | NOT_DECIDED | NOT_DECIDED | Permission/API/storage evidence |
| mood data handling | Sent for advice | Define lifecycle | Ephemeral / retained / other | Advice | User | NOT_DECIDED | NOT_DECIDED | Request/storage evidence |
| chat/advice content handling | Requests exist | Define content lifecycle | Ephemeral / session / history / other | LLM | User | NOT_DECIDED | NOT_DECIDED | Payload/processor/storage |
| history/daily-record handling | Routes/store exist | Define lifecycle | Device / Backend / export / none / other | Storage | User | NOT_DECIDED | NOT_DECIDED | Schema/lifecycle evidence |
| connection/token metadata | Local OAuth support | Define custody/use | Device / secret store / provider / none | Provider/D03 | User | NOT_DECIDED | NOT_DECIDED | OAuth/secret flow |
| diagnostic/log data | Non-product paths exist | Define events/access/redaction | Security / operations / opt-in support / none | Monitoring | User | NOT_DECIDED | NOT_DECIDED | Log schema/sample |
| third-party processors | None approved | Name recipients/purposes | Hosting / health / AI / monitoring / support / none | D03 | User | NOT_DECIDED | NOT_DECIDED | Contracts/data flow |
| LLM/provider data transfer | None approved | Decide transfer model | No LLM / DRC-hosted / third-party / other | Architecture | User | NOT_DECIDED | NOT_DECIDED | Terms/payload evidence |
| encryption in transit | Local HTTP | Approve protocols/endpoints | Provider TLS / proxy TLS / other | D03 | User | NOT_DECIDED | NOT_DECIDED | TLS/runtime evidence |
| encryption at rest | No production store | Define protection | Provider / application / no persistence / other | Storage | User | NOT_DECIDED | NOT_DECIDED | Storage config |
| retention period by data category | Some dev TTLs | Set period/rationale | Ephemeral / session / fixed / until deletion / other | Inventory | User | NOT_DECIDED | NOT_DECIDED | Schedule/enforcement |
| deletion method | Dev cleanup only | Choose user/Backend process | In-app / web / support / automatic / combined | Account/storage | User | NOT_DECIDED | NOT_DECIDED | End-to-end test |
| deletion completion target | None | Set measurable period | Immediate / fixed days / category-specific / other | Deletion | User | NOT_DECIDED | NOT_DECIDED | SLA/completion evidence |
| access/export method | None | Define method | In-app / download / support / N/A | Account | User | NOT_DECIDED | NOT_DECIDED | UX/export evidence |
| account creation/deletion applicability | No lifecycle | Decide account model | None / optional / required / federated | Auth | User | NOT_DECIDED | NOT_DECIDED | Account-flow evidence |
| consent withdrawal behavior | Not approved | Define revoke effects | Stop / disconnect / delete / bounded retain / combined | UX/provider | User | NOT_DECIDED | NOT_DECIDED | Revocation tests |
| incident/contact process | None | Assign response process | Operator / provider-assisted / other | D03 | User | NOT_DECIDED | NOT_DECIDED | Runbook/contact |
| Privacy Policy publisher and URL owner | No URL | Assign author/host/owner | Operator site / managed host / other public URL | Identity | User | NOT_DECIDED | NOT_DECIDED | Public URL/revisions |
| Data safety declaration owner | None | Assign prepare/review/submit/update | User / org role / specialist | Play account | User | NOT_DECIDED | NOT_DECIDED | Console roles/reconciliation |
| Health Apps declaration owner | Pending | Assign prepare/review/submit/update | User / org role / specialist | Health scope | User | NOT_DECIDED | NOT_DECIDED | Role/feature mapping |
| declaration/update review owner | None | Assign recurring review owner | User / release / privacy / joint | GP-5/9 | User | NOT_DECIDED | NOT_DECIDED | Cadence/release gate |

## Google Play policy evidence

### Official-source findings

Accessed 2026-09-19.

| Page title | URL | Official finding used |
| --- | --- | --- |
| Provide information for Google Play's Data safety section | https://support.google.com/googleplay/android-developer/answer/10787469?hl=en | Published apps need accurate Data safety information and a Privacy Policy; third-party SDK behavior and collection/sharing, security, and deletion declarations must be considered. |
| User Data | https://support.google.com/googleplay/android-developer/answer/10144311?hl=en | Personal/sensitive data access, collection, use, and sharing require transparency; applicable prominent disclosure and affirmative consent precede related runtime permission/data access; third-party code remains the developer's responsibility. |
| Provide information for the Health apps declaration form | https://support.google.com/googleplay/android-developer/answer/14738291?hl=en | Published apps, including described testing tracks, complete the Health apps declaration and identify relevant health features/data; Sleep Management is listed. |
| Health Content and Services | https://support.google.com/googleplay/android-developer/answer/16679511?hl=en-GB | Health apps need the declaration and an accessible public Privacy Policy; permissions/disclosures must align and health/medical functionality must not mislead. |

### DRC inference and open work

- A reconciled Privacy Policy and Data safety form are needed before the applicable release gate; neither is complete here.
- Selected third-party SDKs/processors must enter the runtime inventory and declaration assessment.
- DRC appears to be a Sleep Management candidate, but the final category remains `NOT_DECIDED`.
- Health-data and runtime-permission behavior must align with prominent disclosure, consent, policy, and declarations.
- The health-feature Privacy Policy needs a public accessible URL; publisher and owner remain undecided.
- A later review must preserve the boundary that DRC is not presented as medical diagnosis/treatment. Final non-medical disclaimer and store wording belong to GP-5/GP-7.
- These are planning inferences, not legal advice or a claim of compliance completion.

## Decision questionnaire

Unchecked answers remain `NOT_DECIDED`; later selections require exact values and evidence.

### GP0-D03 closed-choice

- [ ] Hosting: PaaS / serverless / container / VM / other / none.
- [ ] Domain: owned custom / provider / none.
- [ ] TLS: provider / load balancer / proxy / other.
- [ ] Region: one / multiple / provider default / other.
- [ ] Authentication: anonymous bounded / attestation / user token / gateway / other.
- [ ] Isolation: accounts/projects / services / configuration / other.
- [ ] Observability: provider / external / self-hosted / minimal.
- [ ] Backup: none / provider / custom / other.
- [ ] Localhost proof: static / runtime / both / other.

### GP0-D03 free-form

- [ ] Provider/account owner; base URL/domain owner; permitted regions.
- [ ] Secret custodian/rotation; deploy/rollback/incident owners.
- [ ] Availability, maintenance, cost ceiling, CORS/ingress/rate limits.

### GP0-D08 closed-choice

- [ ] Account: none / optional / required / federated.
- [ ] Processing: device / DRC Backend / third party / mixed by category.
- [ ] Optionality: required / optional / conditional / not collected by category.
- [ ] LLM: none / DRC-hosted / third-party / other.
- [ ] Deletion: in-app / web / support / automatic / combined.
- [ ] Access/export: in-app / download / support / not applicable.
- [ ] Retention: ephemeral / session / fixed / until deletion / category-specific.
- [ ] Declaration owner: user / organization / specialist / joint.

### GP0-D08 free-form

- [ ] Operator identity; privacy/support contacts; publication countries/regions.
- [ ] Field inventory, purposes, and health/mood/chat/history/token/log handling.
- [ ] Processors, recipients, transfer regions, encryption, and access controls.
- [ ] Retention/deletion targets; withdrawal, account deletion, access/export.
- [ ] Policy publisher/URL owner; declaration, incident, and review owners.
- [ ] Separately obtained legal review, if any.

## Exit criteria

### This control

- [x] Current-state evidence inventory completed.
- [x] D03/D08 fields covered; unanswered decisions explicitly `NOT_DECIDED`.
- [x] Four official sources recorded with access date.
- [x] No product source change or Backend wiring.
- [x] No provider, domain, privacy value, territory, or legal conclusion silently approved.
- [x] Separate user decision authorization required.

### Before D03/D08 can become APPROVED

- User explicitly approves every exact value.
- Approved value, owner, date, and evidence are recorded.
- Runtime behavior, Privacy Policy, Data safety, and Health Apps are reconciled.
- Resulting implementation receives a separate bounded authorization.
