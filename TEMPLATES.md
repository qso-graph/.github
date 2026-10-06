# qso-graph Workflow Templates

Canonical snippets that every qso-graph MCP repo copies into its own
`.github/workflows/*.yml` files. Each repo holds an independent copy
(per-repo isolation; see Patton's review note 2026-05-16 on the
version-drift architecture). When a template changes, every copy is
updated explicitly by a PR per repo.

This file is **the** source of truth. If you change a workflow in a
single repo, update this file first and propagate.

---

## How we develop and release (every qso-graph repo)

KI7MT, 2026-10-06. **Git Flow, lightweight**: two long-lived branches, short-lived work branches,
and a release is one PR into `main`. Proven on adif-mcp 1.2.0.

| Branch | What it is | Who changes it |
|---|---|---|
| **`develop`** | the default branch; where work lands | merged PRs from work branches |
| **`main`** | **exactly the released code**, always | merged release PRs (and security PRs) only |
| `fix/…`, `feat/…`, `docs/…` | one issue's work, branched off `develop` | its author; deleted when merged |
| `security/…` | a security fix, branched off `main` | its author |

### The steps

1. **Plan.** Each repo's next release is a GitHub **milestone** named for its version
   (`adif-mcp 1.2.0`). Issues go into it by lane:

   | Kind | Release |
   |---|---|
   | **Security findings** | **Immediately**, however many: fixed together, released at once (below) |
   | **Bug fixes** | the **next release's** milestone |
   | **Features** | the **next milestone**, or the next release if confident it is ready |

2. **Work.** One branch per issue off `develop`, one PR **into `develop`**: code, tests, and an
   entry under `## [Unreleased]` in `CHANGELOG.md`. **No version bump.** Reviewed, merged. Any number
   of these.
3. **Release**, when every issue in the milestone is closed **and KI7MT says release**. Two PRs:
   1. **Prepare**: a `release/X.Y.Z` branch off `develop`, PR into `develop`: bump the version in
      `pyproject.toml`, `server.json` (two places) and `uv.lock`'s own entry; rename `[Unreleased]`
      to `[X.Y.Z] - date`. Nothing else.
   2. **Release**: PR from **`develop` into `main`**. **Merging it publishes**: `publish.yml` runs on
      the push to `main`, publishes to PyPI and the MCP Registry, verifies both, and tags `vX.Y.Z`.
      Close the milestone when the run is green.

**Security fixes:** a `security/…` branch off **`main`**, with the fix and the patch version bump.
PR it into `main` (merging publishes), then PR **the same branch** into `develop`, so `develop`
has the fix too.

A change that never reaches the published package (tests, scripts, CI, internal docs) still goes
under `[Unreleased]` and counts toward its milestone; it needs no release of its own.

### Repo settings (once per repo, before anything else)

- **Default branch: `develop`.**
- **Merge commits only**: squash and rebase merging off. A squash-merged release PR gives `main` a
  commit `develop` doesn't have, and the branches drift apart.
- **Ruleset "protect main and develop"**, on both: no deletion, no force push, and **a pull request
  required before merging** (zero approvals required: reviews are posted as comments, and KI7MT
  merges). Without the PR rule, a direct push to `main` would skip the `Release PR source` check,
  which runs on pull requests only, and still publish.
- **`main` requires the `Release PR source` check** (`ci.yml`, below): PRs into `main` only from
  `develop` or `security/…`.
- "Automatically delete head branches" may stay on: protected branches can't be deleted.

### Never

- **Never open a PR whose head is `main` or `develop`.** With automatic branch deletion on,
  merging it deletes that branch (this deleted adif-mcp's `main` on 2026-10-06).
- **Never push straight to `main` or `develop`**, and never tag by hand: the tag comes from the
  release run.
- **Never rename `publish.yml`.** PyPI's trusted publishing is bound to the workflow's filename.
- **Never bump a version in a work PR**, or release without KI7MT's go (security excepted).

## A release is done when it's published everywhere

**A release is complete only when PyPI and the Official MCP Registry
both serve the new version** (KI7MT, 2026-09-28). A PyPI release alone is
half a release.

`publish.yml` runs on **every push to `main`** (a merged release PR) and enforces that, in this order:

1. **`security`**: the **release gate** first. The version on `main` (from `pyproject.toml`) must be
   **new**: only a 404 from PyPI counts as "not published", and only `git ls-remote` exit 2 as "no
   such tag"; anything it cannot confirm stops the release (fails closed). `server.json` must match.
   The version is computed here **once** and every later job uses it. Then the security tests.
2. **`publish`**: PyPI, by trusted publishing (OIDC).
3. **`registry-publish`**: the MCP Registry, by GitHub OIDC.
4. **`verify`**: poll PyPI and the Registry until both report the version. **If either doesn't
   within 10 minutes, the run fails.**
5. **`tag`**: tag `vX.Y.Z` on the released commit. A workflow's own tag push triggers nothing, so
   the tag comes last. If it fails after a green `verify`, the release **is** published; re-run it.

**A green run means published everywhere. A red run means the release
isn't done**, whichever step went red. Fix it and finish it; don't leave
it for the next release.

Why this exists: the Registry was never checked. On 2026-09-28 every
qso-graph server in it was behind PyPI (solar-mcp: 0.2.1 on PyPI, 0.1.1 in
the Registry since March), and no run had failed.

### The canonical `publish.yml`

Copy it whole; change nothing but the security-test path if the repo's differs. From adif-mcp
(release 1.2.0, the first run of this flow, green end to end).

```yaml
name: Publish to PyPI

# The release flow (qso-graph/.github TEMPLATES.md): work lands on `develop`; a release is a
# PR from `develop` into `main`, and merging it publishes. `main` is always the released code.
on:
  push:
    branches: [ main ]

concurrency:
  group: publish
  cancel-in-progress: false

permissions:
  contents: read

jobs:
  security:
    name: Security gate
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - uses: actions/checkout@v4

      # main changes only by a release PR, so main's version must be new. PyPI publishes
      # pyproject's version and the Registry server.json's, so they must agree too.
      # Computed once; every later job uses this value (needs.security.outputs.version).
      # The gate fails closed: anything it cannot confirm stops the release.
      - name: The version on main is new and consistent
        id: version
        run: |
          VERSION="$(grep -m1 '^version' pyproject.toml | cut -d'"' -f2)"
          PACKAGE="$(jq -r '.packages[0].identifier' server.json)"
          echo "pyproject=${VERSION} server.json=$(jq -r '.version' server.json)/$(jq -r '.packages[0].version' server.json)"
          if [ "$(jq -r '.version' server.json)" != "$VERSION" ] || [ "$(jq -r '.packages[0].version' server.json)" != "$VERSION" ]; then
            echo "FAIL: server.json does not match pyproject.toml version ${VERSION}"
            exit 1
          fi
          # Only a 404 means "not published yet"; unreachable or 5xx is not a yes.
          CODE="$(curl -s -o /dev/null -w '%{http_code}' "https://pypi.org/pypi/${PACKAGE}/${VERSION}/json")"
          case "$CODE" in
            404) echo "PyPI: ${PACKAGE} ${VERSION} is new" ;;
            200) echo "FAIL: ${PACKAGE} ${VERSION} is already on PyPI. main changes only by a release PR with a new version."; exit 1 ;;
            *)   echo "FAIL: PyPI returned ${CODE}; cannot confirm ${VERSION} is new"; exit 1 ;;
          esac
          # git ls-remote --exit-code: 2 means no such tag; anything else (0, 128) stops.
          set +e
          git ls-remote --exit-code --tags origin "refs/tags/v${VERSION}" > /dev/null
          RC=$?
          set -e
          case "$RC" in
            2) echo "tag v${VERSION} does not exist yet" ;;
            0) echo "FAIL: tag v${VERSION} already exists"; exit 1 ;;
            *) echo "FAIL: could not check tags (git ls-remote exited ${RC})"; exit 1 ;;
          esac
          echo "version=${VERSION}" >> "$GITHUB_OUTPUT"


      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -e ".[test]"

      - name: Security tests
        run: python -m pytest test/test_security.py -v

      - name: Static security checks
        run: |
          ! grep -rn "subprocess\|shell=True" src/ --include="*.py"
          ! grep -rn 'http://[^l]' src/ --include="*.py"
          ! grep -rni "print.*password\|print.*secret" src/ --include="*.py"
          echo "Static checks passed"

  publish:
    name: Build and publish to PyPI
    needs: security
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install build dependencies
        run: pip install build

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1

  # ---------------------------------------------------------------------------
  # Registry-publish — pushes server.json to the Official MCP Registry after
  # PyPI publish succeeds, so discovery surfaces stay in sync with PyPI.
  # Canonical template: https://github.com/qso-graph/.github/blob/main/TEMPLATES.md
  # ---------------------------------------------------------------------------
  registry-publish:
    name: Publish to MCP Registry
    needs: [security, publish]  # waits for PyPI publish to succeed
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

      - name: Set server.json to the released version
        run: |
          VERSION="${{ needs.security.outputs.version }}"
          echo "Setting server.json to ${VERSION}"
          jq --arg v "$VERSION" \
             '.version = $v | .packages[0].version = $v' \
             server.json > /tmp/server.json
          mv /tmp/server.json server.json
          cat server.json

      # The Registry checks PyPI itself and refuses a version PyPI isn't
      # serving yet, which can lag the upload by a minute or more.
      - name: Wait until PyPI serves this version
        run: |
          VERSION="${{ needs.security.outputs.version }}"
          PACKAGE="$(jq -r '.packages[0].identifier' server.json)"
          for i in $(seq 1 40); do
            if curl -fsS "https://pypi.org/pypi/${PACKAGE}/${VERSION}/json" > /dev/null; then
              echo "PyPI serves ${PACKAGE} ${VERSION}"
              exit 0
            fi
            echo "attempt ${i}: PyPI doesn't serve ${PACKAGE} ${VERSION} yet"
            sleep 15
          done
          echo "FAIL: PyPI never served ${PACKAGE} ${VERSION}"
          exit 1

      - name: Authenticate to MCP Registry (GitHub OIDC)
        run: ./mcp-publisher login github-oidc

      # Retries ride out the Registry's own transient failures. Before each
      # retry, check whether an earlier attempt landed despite the error.
      - name: Publish to MCP Registry
        run: |
          VERSION="${{ needs.security.outputs.version }}"
          NAME="$(jq -r '.name' server.json)"
          REGISTRY="https://registry.modelcontextprotocol.io/v0/servers?search=${NAME}&version=latest"
          for i in 1 2 3 4 5; do
            if ./mcp-publisher publish; then
              exit 0
            fi
            echo "attempt ${i} failed; retrying in $((i * 30)) s"
            sleep $((i * 30))
            REG="$(curl -fsS "$REGISTRY" | jq -r --arg n "$NAME" '[.servers[] | select(.server.name == $n) | .server.version][0] // empty' || true)"
            if [ "$REG" = "$VERSION" ]; then
              echo "The Registry already has ${NAME} ${VERSION}; an earlier attempt landed"
              exit 0
            fi
          done
          echo "FAIL: the MCP Registry refused the publish 5 times"
          exit 1

  # ---------------------------------------------------------------------------
  # Verify — a release is complete only when PyPI AND the MCP Registry both
  # serve the tagged version. If either doesn't within 10 minutes, this run
  # fails: a green run means published everywhere, a red one means not done.
  # ---------------------------------------------------------------------------
  verify:
    name: Verify PyPI and MCP Registry
    needs: [security, registry-publish]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - name: PyPI and Registry serve the released version
        run: |
          VERSION="${{ needs.security.outputs.version }}"
          PACKAGE="$(jq -r '.packages[0].identifier' server.json)"
          NAME="$(jq -r '.name' server.json)"
          REGISTRY="https://registry.modelcontextprotocol.io/v0/servers?search=${NAME}&version=latest"
          for i in $(seq 1 40); do
            PYPI="$(curl -fsS "https://pypi.org/pypi/${PACKAGE}/json" | jq -r '.info.version' || true)"
            REG="$(curl -fsS "$REGISTRY" | jq -r --arg n "$NAME" '[.servers[] | select(.server.name == $n) | .server.version][0] // empty' || true)"
            echo "attempt ${i}: PyPI=${PYPI:-none} Registry=${REG:-none} want=${VERSION}"
            if [ "$PYPI" = "$VERSION" ] && [ "$REG" = "$VERSION" ]; then
              echo "Published everywhere: ${PACKAGE} ${VERSION} on PyPI and ${NAME} ${VERSION} in the MCP Registry"
              exit 0
            fi
            sleep 15
          done
          echo "FAIL: release incomplete. PyPI=${PYPI:-none} Registry=${REG:-none}, expected ${VERSION}"
          exit 1

  # ---------------------------------------------------------------------------
  # Tag the release, once it is published everywhere. The tag marks the commit on
  # main that was released; nothing is triggered by it. If this job fails after a
  # green verify, the release IS published: re-running this job is safe.
  # ---------------------------------------------------------------------------
  tag:
    name: Tag the release
    needs: [security, verify]
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v5

      - name: Create and push vX.Y.Z
        run: |
          VERSION="${{ needs.security.outputs.version }}"
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git tag -a "v${VERSION}" -m "${GITHUB_REPOSITORY#*/} ${VERSION}" "$GITHUB_SHA"
          git push origin "v${VERSION}"
```

### The `Release PR source` check (`ci.yml`)

```yaml
  # main takes a release PR from develop, or a security branch, and nothing else:
  # merging into main publishes. Required on main by its branch protection.
  release-source:
    name: Release PR source
    if: github.event_name == 'pull_request' && github.base_ref == 'main'
    runs-on: ubuntu-latest
    steps:
      - run: |
          case "${{ github.head_ref }}" in
            develop|security/*) echo "ok: ${{ github.head_ref }} -> main" ;;
            *) echo "main takes a release PR from develop, or a security/ branch"; exit 1 ;;
          esac
```

`ci.yml` and any other CI workflow run on `push` to both `main` and `develop`, and on every PR.

---

## Registry-publish job

**Purpose**: after a successful PyPI publish (triggered by a merged release PR on `main`), publish the same version to the [Official MCP Registry](https://registry.modelcontextprotocol.io)
so discovery surfaces stay in sync with PyPI.

**Auth model**: GitHub OIDC. No PATs or registry tokens to manage; the
workflow's identity is bound to the repository and the workflow file.

It is in the canonical `publish.yml` above (`registry-publish`).

### Why wait and retry

The first run of this job (netlogger-mcp v0.1.1, 2026-09-28) failed
twice, and both failures needed a manual re-run:

1. **PyPI lag.** The Registry answered "version '0.1.1' was not found
   (404)" because it checks PyPI itself, seconds after the upload. The
   wait step closes that.
2. **Registry outage.** On the re-run, the Registry's own database
   refused connections. The retries ride that out.

Before each retry the job checks whether the Registry already has the
version, in case an attempt landed but its reply was lost; retrying that
would only fail on "already exists". Either way, the `verify` job still
decides whether the release is done.

### Requirements per repo

1. `server.json` must exist at the repo root with the canonical
   structure (name, description, repository, version, packages).
   Use `mcp-publisher init` to generate the first time, then commit it.
2. `server.json`'s `name` field must use the
   `io.github.qso-graph/<repo-name>` convention.
3. `server.json`'s `packages[0].registryType` must be `pypi`.
4. The PyPI `publish` job must complete successfully before
   `registry-publish` runs (the `needs: publish` gate enforces this).

### Why the "set server.json" step

The release gate already refuses a `server.json` that doesn't match `pyproject.toml`, so the
committed file is right. The step writes the gate's version into `version` and
`packages[0].version` in memory anyway, so the Registry can only ever receive the version PyPI was
given. The committed file is not modified by CI.

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
[![MCP Registry](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fregistry.modelcontextprotocol.io%2Fv0%2Fservers%3Fsearch%3Dio.github.qso-graph%2F<package-name>%26version%3Dlatest&query=%24.servers%5B0%5D.server.version&label=MCP%20Registry&color=blue)](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.qso-graph/<package-name>&version=latest)
```

Replace `<package-name>` with the PyPI name in two places per badge.
The Registry badge is a [shields.io dynamic JSON badge](https://shields.io/badges/dynamic-json-badge)
that reads the `version` field from the first matching Registry entry.

### Honest framing

The 2026-05-16 rollout used **forward-only sync** (per Patton's review):
Registry entries were left stale until each server's next real release.
That left every server behind for months, with nothing failing
(2026-09-28). **Superseded (KI7MT, 2026-09-28):** every MCP is brought up
to date in one sweep, each release carrying the real changes of the sweep
(README layout, `server.json`, the release gates), and from then on the
`verify` job keeps PyPI and the Registry in step. The badges stay as a
visible check.

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
- **Release gates** — the tag must match `pyproject.toml`, and a
  `verify` job fails the release unless PyPI and the MCP Registry
  both serve the new version.
```

---

## uv: how every qso-graph repo is installed, run and developed

We use [uv](https://docs.astral.sh/uv/), and we recommend it to users. Proposed by
[@MicaelJarniac](https://github.com/MicaelJarniac) in
[qrz-mcp#8](https://github.com/qso-graph/qrz-mcp/issues/8).

### For users (README)

**Install** — `uvx` first (runs without an install step, always the current release), `pip`
second:

```bash
uvx <package>            # run it; nothing to install
pip install <package>    # or install it into your own environment
```

**MCP client config** — `uvx`, so there's no PATH to get right:

```json
{
  "mcpServers": {
    "<short-name>": {
      "command": "uvx",
      "args": ["<package>"]
    }
  }
}
```

(VS Code uses `"servers"` instead of `"mcpServers"`.) Add one line after the configs: *installed
with pip? use `"command": "<package>"` instead.* Servers that need environment variables keep
their `"env"` block.

Command-line tools (`qso-auth`, `ionis-download`): `uv tool install <package>`, which puts the
commands on PATH.

### For development (README "Development" section)

```bash
git clone https://github.com/qso-graph/<repo>.git
cd <repo>
uv sync --group dev
uv run pytest
```

### pyproject.toml

Test tools are declared, not only installed by CI:

```toml
[dependency-groups]
dev = ["pytest>=8"]
```

Add others only if the tests use them (`pytest-asyncio` only with `async` tests). **`uv.lock` is
committed**, so CI and every developer resolve the same versions. The build backend stays
**hatchling**, and `publish.yml` is unchanged.

### ci.yml

```yaml
jobs:
  test:
    name: pytest (${{ matrix.python-version }})
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v5

      - uses: astral-sh/setup-uv@v6
        with:
          python-version: ${{ matrix.python-version }}
          enable-cache: true

      - name: Install (locked)
        run: uv sync --group dev --frozen

      - name: Unit tests
        run: uv run pytest tests --ignore=tests/test_security.py -v

      - name: Security tests
        run: uv run pytest tests/test_security.py -v
```

`--frozen` fails CI if `uv.lock` is out of date with `pyproject.toml`, so the lock can't drift.
Repos that also test Windows or macOS keep their `os` matrix.

---

## Rollout checklist (per repo)

In this order. Settings first, so nothing can be deleted or squashed while the rest changes.

- [ ] **Ruleset "protect main and develop"** on `main` and `develop`: deletion, non-fast-forward,
      and **pull request required** (0 approvals)
- [ ] **Merge commits only** (squash and rebase off)
- [ ] **`develop`** created from `main`, and made the **default branch**
- [ ] One PR into `develop`: the canonical **`publish.yml`**, the **`Release PR source`** job in
      `ci.yml`, CI on `push` to `main` and `develop`
- [ ] `main` requires the `Release PR source` check (after that PR has run once, so the check exists)
- [ ] `server.json` at repo root, `name` `io.github.qso-graph/<repo-name>`, `packages[0]`
      `registryType: pypi`, `identifier` = the PyPI name; `mcp-publisher validate` passes
- [ ] `CHANGELOG.md` has `## [Unreleased]` at the top
- [ ] README has the PyPI and MCP Registry badges
- [ ] **uv**: `[dependency-groups] dev`, `uv.lock` committed, `ci.yml` on `setup-uv` with
      `uv sync --group dev --frozen`; README uses `uvx` and `uv sync` / `uv run pytest`
- [ ] The next release goes through the flow, and its run is green through `tag`

---

## Related references

- Official MCP Registry: https://registry.modelcontextprotocol.io
- `mcp-publisher` source: https://github.com/modelcontextprotocol/registry
- Publishing quickstart: https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/quickstart.mdx
- GitHub Actions guide: https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/github-actions.mdx
- Patton's architecture review (2026-05-16 inbox): per-repo copy preferred over shared workflow — same logic as `ci.yml` decision; publish workflows have higher consequence so isolation matters more
- `mcp.so` sync: pulls from the Official Registry on its own cadence; no separate publish step needed (verify periodically)
- Anthropic Connector List: separate manual-review process (not in scope for this automation)
