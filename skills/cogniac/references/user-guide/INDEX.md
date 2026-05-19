# Cogniac User Guide — Index

Files are flat. Grep across the dir:

```bash
grep -rl "term" references/user-guide/
```

Per-endpoint API duplicates (`applications-create`, `subjects-retrieve`, etc.)
have been omitted — they live in `references/api/` with full schemas.

## Intent map (common tasks → file)

- **Get started / orient a new user** → `getting-started.md`, `cloudcore-overview.md`, `machine-learning-concepts.md`
- **Pick the right application type** → `application-types.md`, then the per-type file (`classification-application.md`, `box-detection-application.md`, `area-detection-application.md`, `count-application.md`, `point-detection.md`, `point-count-app.md`, `optical-character-recognition-ocr-application.md`, `segmentation-application.md`)
- **Create an app, step-by-step** → `creating-a-<type>-application.md` (classification, detection, box-detection, area-detection, count, point-detection, OCR)
- **Label images & train** → `tutorial-how-to-label-images-and-train-models.md`
- **Deploy a workflow** → `deployments-quickstart-guide.md`, `cogniac-workflow-creation-and-deployment.md`, `how-to-create-a-workflow.md`, `how-to-create-a-deployment-group.md`, `how-to-deploy-a-workflow-to-an-edgeflow.md`, `workflow-update.md`
- **Best practices** → `cogniac-best-practices-iron-fist.md`, `cogniac-box-detection-best-practices.md`, `cogniac-rare-subject-mining-best-practices.md`, `best-practices-for-camera-selection-and-positioning.md`
- **API / auth / errors (concepts)** → `api-overview.md`, `authentication.md`, `pagination.md`, `api-errors.md`
- **SDK overviews** → `cogniac-python-sdk.md`, `cogniac-c-sdk.md` (C#)
- **CLI** → `cogniac-cli.md`
- **Meraki integration** → `meraki-ai-quick-start-guide.md`, `meraki-api-advanced-setup-guide.md`, `meraki-ai-troubleshooting-guide.md`
- **EdgeFlow networking / connectivity** → `cogniac-edgeflow-network-faq.md`, `checking-ef-basic-connectivity.md`, `edgeflow-security-updates.md`
- **Access control / users / tenants** → `create-and-maintain-an-access-control-list-acl.md`, `application-managers.md`, `user-authentication.md`, `cogniac-users.md`, `invitations-1.md`, `tenant-home.md`, `tenant-expiration.md`, `go-to-a-tenant.md`
- **FAQ / troubleshooting** → `i-keep-getting-errors.md`, `do-cogniac-access-tokens-expire.md`, `are-there-data-limits-or-api-rate-limits.md`, `how-does-cogniac-handle-downtime.md`, `data-retention.md`, `data-security-and-encryption.md`, `what-characters-and-languages-are-supported.md`, `which-timezone-is-used-throughout-the-cogniac-system.md`, `do-you-have-sdk.md`, `how-do-i-report-bugs-or-feature-requests.md`
- **Release history** → `release.md`, `release-notes-<year>.md` (2020–2025)

## Sections (upstream nav order)

### Introduction
- `cloudcore-overview.md`
- `machine-learning-concepts.md`
- `user-login.md`
- `tenant-home.md`
- `usersnap-feature.md`
- `cogniac-subjects.md`
- `subject-media-associations.md`
- `getting-started.md`
- `application-managers.md`
- `invitations-1.md` — Invitation to Tenant
- `go-to-a-tenant.md`
- `user-authentication.md`
- `paygo-subscription.md`
- `create-and-maintain-an-access-control-list-acl.md`
- `tenant-expiration.md`
- `associate-media-with-subject.md`
- `pixel-measurement-tool.md`

### Onboarding Documentation
- `replay-feature-from-the-antire-pipeline.md` — Replay from the root application
- `leaderboard-feature-summary.md`
- Vision AI Applications Demo:
  - `creating-a-classification-application.md`
  - `creating-a-detection-application.md`
  - `creating-a-box-detection-application.md`
  - `creating-an-area-detection-application.md`
  - `creating-a-count-application.md`
  - `creating-an-optical-character-recognition-app-ocr.md`
  - `creating-a-point-detection-application.md`
- `tutorial-how-to-label-images-and-train-models.md`
- Tutorials → `subjects-1.md` — Subjects
- Upgrade Plan:
  - `upgrade-starter-plan.md`
  - `upgrade-to-enterprise-plan.md`
  - `upgrade-to-pro-plan.md`
- `guided-onboarding-tour-self-serve-plan.md`

### Application Types
- `application-types.md` — overview
- Vision AI Applications:
  - `classification-application.md`
  - `detection-application.md`
  - `area-detection-application.md`
  - `point-detection.md`
  - `box-detection-application.md`
  - `count-application.md`
  - `optical-character-recognition-ocr-application.md`
  - `segmentation-application.md`
  - `point-count-app.md`
- Media Processor Applications → `integration-app-1.md` — Integration App RBAC
- Input/Output Applications → `http-input-application-replicas.md`
- `how-to-invite-a-new-user-to-tryout-cogniac-for-30-days-trial.md`

### Deployments
- `deployments-quickstart-guide.md`
- `cogniac-workflow-creation-and-deployment.md`
- `workflow-update.md`
- `how-to-create-a-workflow.md`
- `how-to-create-a-deployment-group.md`
- `how-to-deploy-a-workflow-to-an-edgeflow.md`

### Best Practices
- `cogniac-best-practices-iron-fist.md`
- `cogniac-rare-subject-mining-best-practices.md`
- `cogniac-box-detection-best-practices.md`
- `best-practices-for-camera-selection-and-positioning.md`

### Meraki
- `meraki-ai-quick-start-guide.md`
- `meraki-api-advanced-setup-guide.md`
- `meraki-ai-troubleshooting-guide.md`

### Cogniac API (concepts & overviews only)
Per-endpoint detail lives in `../api/` — these are conceptual framings.

- `api-overview.md`
- `authentication.md`
- `pagination.md`
- `api-errors.md`
- `cogniac-python-sdk.md`
- `cogniac-c-sdk.md` — C# SDK
- `tenants.md` — overview
- `cogniac-users.md`
- `users.md` — overview
- `applications.md` — overview
- `subjects.md` — overview
- `media.md` — overview
- `gateways.md` — CloudCore management of EdgeFlows
- `network-cameras.md` — overview
- `cloudflow-api.md` — CloudFlow APIs

### Cogniac CLI
- `cogniac-cli.md`

### Knowledge Base
- `edgeflow-security-updates.md`
- `data-retention.md`
- `what-characters-and-languages-are-supported.md`
- `how-do-i-report-bugs-or-feature-requests.md`
- `do-you-have-sdk.md`
- `which-timezone-is-used-throughout-the-cogniac-system.md`
- `do-cogniac-access-tokens-expire.md`
- `i-keep-getting-errors.md`
- `checking-ef-basic-connectivity.md`
- `data-security-and-encryption.md`
- `are-there-data-limits-or-api-rate-limits.md`
- `how-does-cogniac-handle-downtime.md`
- `cogniac-edgeflow-network-faq.md`

### Contact Us
- `contact-us.md`

### Demos and Tutorials
- `demo-tutorials.md`

