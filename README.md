# Cogniac Skills

Public agent skills for working with the [Cogniac](https://www.cogniac.io/) computer
vision platform. Install via the [skills.sh](https://skills.sh/) CLI to give your
coding or autonomous agent first-class knowledge of the Cogniac SDK, CLI, and public API.

This repository is part of the broader effort to make Cogniac the best platform for
agentic real-world computer vision development — see the umbrella tracker at
[Cogniac/CloudCore-Product#984](https://github.com/Cogniac/CloudCore-Product/issues/984)
and the public-skill workstream at
[Cogniac/CloudCore-Product#983](https://github.com/Cogniac/CloudCore-Product/issues/983).

## Available skills

| Skill | What it teaches |
|-------|-----------------|
| [`cogniac`](skills/cogniac/) | Installing the `cogniac` pip package, authenticating, using the Python SDK and `cogniac` CLI, and working with the Cogniac public API end-to-end. |

More skills will follow as the platform's agentic surface area grows.

## Install

Install all skills in this repo:

```bash
npx skills add Cogniac/skills
```

Install a specific skill:

```bash
npx skills add Cogniac/skills --skill cogniac
```

Install globally (available across all projects):

```bash
npx skills add Cogniac/skills --skill cogniac -g
```

Install for a specific agent (e.g. Claude Code):

```bash
npx skills add Cogniac/skills --skill cogniac -a claude-code
```

See the [`skills` CLI docs](https://skills.sh/docs) for more options.

## Authoring new skills

Each skill lives in its own directory under `skills/<name>/` and must contain a
`SKILL.md` with YAML frontmatter:

```markdown
---
name: my-skill
description: One-line description of when an agent should activate this skill.
---

# My Skill

Body of the skill — instructions, examples, references.
```

Use `npx skills init <name>` from this repo's root to scaffold a new skill.

See [`SKILL_TEMPLATE.md`](SKILL_TEMPLATE.md) for the in-repo template.

## Contributing

This repository is the canonical source for Cogniac-authored agent skills. Open a PR
against `main` for additions or improvements; CI will validate skill structure on
merge (TODO: wire up).

## Support

Questions about the Cogniac platform: [support@cogniac.co](mailto:support@cogniac.co)
or the public docs at [docs.cogniac.io](https://docs.cogniac.io/).
