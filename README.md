# Cogniac Skills

[![skills.sh](https://skills.sh/b/Cogniac/skills)](https://skills.sh/Cogniac/skills)

Agent skills for interacting with the [Cogniac](https://www.cogniac.io/) AI computer vision platform.

Skills are folders of instructions, scripts, and resources that agents load dynamically to perform specialized tasks. This repository packages Cogniac-specific knowledge — CLI usage, SDK patterns, platform concepts and documentation — so agents can productively query and manage all Cogniac platform functionality.

## What's included

- [`skills/cogniac`](./skills/cogniac) — Core skill covering the `cogniac` CLI, Python SDK, and public API. Use for EdgeFlow/CloudFlow management, tenant/app/subject/media operations, VLM-assisted labeling, camera inventory, deployments, and other CloudCore operations via direct public-API access.

## Install

### `skills` CLI

```
npx skills add Cogniac/skills --skill cogniac
```

Or to install everything in the collection:

```
npx skills add Cogniac/skills
```

### Claude Code (plugin marketplace)

Register this repository as a plugin marketplace, then install:

```
/plugin marketplace add Cogniac/skills
/plugin install cogniac-skills@cogniac-agent-skills
```

### Manual

Copy the desired skill folder (e.g. `skills/cogniac`) into your agent's skills directory — for Claude Code, that's `~/.claude/skills/`.

## Prerequisites

Most skills here assume the `cogniac` Python package is installed and credentials are configured. The skill will help install if it required.

## Links

- Cogniac Platform: <https://www.cogniac.io/>
- Platform docs: <https://docs.cogniac.io/>
- Python SDK: <https://github.com/Cogniac/cogniac-sdk-py>
- PyPI: <https://pypi.org/project/cogniac/>
- Support: support@cogniac.ai

## License

Apache 2.0 — see [LICENSE](./LICENSE).
