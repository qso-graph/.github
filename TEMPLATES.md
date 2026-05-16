# qso-graph Workflow Templates

Canonical snippets that the 13 qso-graph MCP repos copy into their own
`.github/workflows/*.yml` files. Each repo holds an independent copy
(per-repo isolation; see Patton's review note 2026-05-16 on the
version-drift architecture). When a template changes, every copy is
updated explicitly by a PR per repo.

This file is **the** source of truth. If you change a workflow in a
single repo, update this file first and propagate.

---

## Registry-publish job

**Purpose**: after a successful PyPI publish (triggered by a `v*` git
tag), publish the same version to the [Official MCP Registry](https://registry.modelcontextprotocol.io)
so discovery surfaces stay in sync with PyPI.

**Auth model**: GitHub OIDC. No PATs or registry tokens to manage; the
workflow's identity is bound to the repository and the workflow file.

**Drop into each repo's `publish.yml`** as a new job, after the
existing `publish` job:

```yaml
  registry-publish:
    name: Publish to MCP Registry
    needs: publish  # waits for PyPI publish to succeed
    runs-on: ubuntu-latest
    permissions:
      id-token: write   # GitHub OIDC
      contents: read

    steps:
      - uses: actions/checkout@v5

      - name: Install jq (server.json bump)
        run: sudo apt-get update && sudo apt-get install -y jq

      - name: Install mcp-publisher
        run: |
          curl -L "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/').tar.gz" | tar xz mcp-publisher
          ./mcp-publisher --help > /dev/null  # smoke test

      - name: Bump server.json to tag version
        run: |
          TAG_VERSION="${GITHUB_REF_NAME#v}"
          echo "Setting server.json to ${TAG_VERSION}"
          jq --arg v "$TAG_VERSION" \
             '.version = $v | .packages[0].version = $v' \
             server.json > /tmp/server.json
          mv /tmp/server.json server.json
          cat server.json

      - name: Authenticate to MCP Registry (GitHub OIDC)
        run: ./mcp-publisher login github-oidc

      - name: Publish to MCP Registry
        run: ./mcp-publisher publish
```

### Requirements per repo

1. `server.json` must exist at the repo root with the canonical
   structure (name, description, repository, version, packages).
   Use `mcp-publisher init` to generate the first time, then commit it.
2. `server.json`'s `name` field must use the
   `io.github.qso-graph/<repo-name>` convention.
3. `server.json`'s `packages[0].registryType` must be `pypi`.
4. The PyPI `publish` job must complete successfully before
   `registry-publish` runs (the `needs: publish` gate enforces this).

### Why the bump step

The committed `server.json` has the version at the time it was last
committed — which lags behind tag pushes. The bump step takes the tag
(`v1.2.3` → `1.2.3`) and writes it into both `version` and
`packages[0].version` in-memory before publish. The committed file is
not modified by CI.

### Why OIDC and not a PAT

OIDC binds the workflow's identity to the repository and workflow file.
No long-lived token to rotate, no credential to leak. The Registry
verifies that the publishing identity matches the namespace in
`server.json` (`io.github.qso-graph/*`).

---

## README badge — PyPI + Registry version

**Purpose**: make version drift between PyPI and the Registry
immediately visible in the repo's README. If the Registry is stale,
the badges show different numbers.

```markdown
[![PyPI](https://img.shields.io/pypi/v/<package-name>?label=PyPI&color=blue)](https://pypi.org/project/<package-name>/)
[![MCP Registry](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fregistry.modelcontextprotocol.io%2Fv0%2Fservers%3Fsearch%3D<package-name>&query=%24.servers%5B0%5D.server.version&label=MCP%20Registry&color=blue)](https://registry.modelcontextprotocol.io/v0/servers?search=<package-name>)
```

Replace `<package-name>` with the PyPI name in two places per badge.
The Registry badge is a [shields.io dynamic JSON badge](https://shields.io/badges/dynamic-json-badge)
that reads the `version` field from the first matching Registry entry.

### Honest framing

This rollout uses **forward-only sync** (per Patton 2026-05-16 review):
existing Registry entries stay stale until each server's next real
release naturally catches them up. The badge difference is the visible
signal that staleness exists. Don't tag content-free releases just to
sync — that pollutes version history.

---

## CHANGELOG entry — registry sync mechanism

Add this to every repo's CHANGELOG when the registry-publish job lands:

```markdown
### Added (CI hygiene)

- **MCP Registry sync** — `publish.yml` now publishes to the [Official MCP Registry](https://registry.modelcontextprotocol.io)
  after each PyPI publish, using GitHub OIDC for auth. Triggered on
  `v*` tag push; no manual steps. Pattern documented in
  [qso-graph/.github/TEMPLATES.md](https://github.com/qso-graph/.github/blob/main/TEMPLATES.md).
- **Registry version badge** in README — PyPI and Registry versions
  are visible side-by-side so any drift between publishing surfaces
  is immediately apparent.

### Known drift

Earlier releases of this server (before this version) may show as
**stale** in the Official MCP Registry. The Registry catches up on
the next real release; we don't tag content-free releases purely for
hygiene.
```

---

## Rollout checklist (per repo)

When applying this template to a new repo:

- [ ] `server.json` exists at repo root (run `mcp-publisher init` if not)
- [ ] `server.json` `name` is `io.github.qso-graph/<repo-name>`
- [ ] `server.json` `packages[0].registryType` is `pypi`
- [ ] `server.json` `packages[0].identifier` matches the PyPI name
- [ ] `.github/workflows/publish.yml` has the `registry-publish` job appended
- [ ] `README.md` has both PyPI and MCP Registry badges
- [ ] `CHANGELOG.md` has the "MCP Registry sync" entry in the upcoming release
- [ ] No other YAML changes; per-repo independence preserved

---

## Related references

- Official MCP Registry: https://registry.modelcontextprotocol.io
- `mcp-publisher` source: https://github.com/modelcontextprotocol/registry
- Publishing quickstart: https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/quickstart.mdx
- GitHub Actions guide: https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/github-actions.mdx
- Patton's architecture review (2026-05-16 inbox): per-repo copy preferred over shared workflow — same logic as `ci.yml` decision; publish workflows have higher consequence so isolation matters more
- `mcp.so` sync: pulls from the Official Registry on its own cadence; no separate publish step needed (verify periodically)
- Anthropic Connector List: separate manual-review process (not in scope for this automation)
