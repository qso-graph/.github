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

KI7MT, 2026-10-25. **One working branch, and a release is a button.** Merging publishes
nothing; `publish.yml` fires on `workflow_dispatch` with the version typed in.

> **This replaced Git Flow (KI7MT, 2026-10-06), and the reason is worth keeping.** Under that
> flow `publish.yml` triggered on a push to `main`, so *merging the release PR was the act of
> publishing*. That forced **two pull requests for every release** — one to prepare the version
> on `develop`, a second to merge `develop` into `main` and ship it. All 22 server repositories
> moved on 2026-10-25. Across those 22 merges into `main`, **zero publish runs**, where each
> repository's two previous merges have one.

| Branch | What it is | Who changes it |
|---|---|---|
| **`main`** | the default branch; where work lands. **Merging it publishes nothing** | merged PRs from work branches |
| `fix/…`, `feat/…`, `docs/…`, `security/…` | one issue's work, branched off `main` | its author; deleted when merged |

There is no `develop` and no release branch. A release is not a branch or a merge: it is
**Actions → Publish to PyPI → Run workflow**, with the version typed in.

### The steps

1. **Plan.** Each repo's next release is a GitHub **milestone** named for its version
   (`adif-mcp 1.2.0`). Issues go into it by lane:

   | Kind | Release |
   |---|---|
   | **Security findings** | **Immediately**, however many: fixed together, released at once (below) |
   | **Bug fixes** | the **next release's** milestone |
   | **Features** | the **next milestone**, or the next release if confident it is ready |

2. **Work.** One branch per issue off `main`, one PR **into `main`**: code, tests, and an
   entry under `## [Unreleased]` in `CHANGELOG.md`. **No version bump.** Reviewed, merged. Any
   number of these. Merging publishes nothing, so this needs no ceremony.
3. **Release**, when every issue in the milestone is closed **and KI7MT says release**. One PR,
   then a button:
   1. **Prepare**: one PR into `main` that bumps the version in `pyproject.toml`, `server.json`
      (two places) and `uv.lock`'s own entry, and renames `[Unreleased]` to `[X.Y.Z] - date`.
      Nothing else. Merging it publishes nothing.
   2. **Release**: **Actions → Publish to PyPI → Run workflow**, and type the version. It must
      match `pyproject.toml` — typed because it is a decision, so a slip names a version that is
      not in the tree rather than shipping whatever happens to be on `main`. The run publishes to
      PyPI and the MCP Registry, verifies both, and tags `vX.Y.Z`. Close the milestone when it is
      green.

**Security fixes** are no longer a separate lane. A `security/…` branch off `main`, one PR into
`main`, then release when it is in. There is no second branch to forward-port it to, which was
the whole cost of the old `security/…` rule.

A change that never reaches the published package (tests, scripts, CI, internal docs) still goes
under `[Unreleased]` and counts toward its milestone; it needs no release of its own.

### Repo settings (once per repo, before anything else)

- **Default branch: `main`.**
- **Merge commits only**: squash and rebase merging off.
- **Ruleset protecting `main`**: no deletion, no force push, and **a pull request required before
  merging** (zero approvals required: reviews are posted as comments, and KI7MT merges).
- **`main` requires the `ci-all-green` check** (`ci.yml`, below). This is what replaced
  `Release PR source`, and the swap has an ordering trap — see *Migrating a repo* below.
- **The `pypi` Environment: Deployment branches → Selected → `main`.** Not optional, and not the
  same thing as the workflow's own check. `workflow_dispatch` has a *"Use workflow from"* branch
  picker that `push: [main]` never had, so without this rule a dispatch from any branch would
  build that branch, publish it to PyPI and tag it. The workflow refuses a non-`main` ref too,
  but **the Environment is the lock**: a workflow file is editable by anyone who can open a pull
  request, an Environment setting is not. The workflow check exists so a refused run *says* what
  was wrong, because an Environment rejection does not.
- "Automatically delete head branches" may stay on: protected branches can't be deleted. (It is
  why `develop` survived its final merge in all 22 repos — the ruleset blocked the auto-delete.)

### Never

- **Never open a PR whose head is `main`.** With automatic branch deletion on, merging it
  deletes that branch (this deleted adif-mcp's `main` on 2026-10-06).
- **Never push straight to `main`**, and never tag by hand: the tag comes from the release run.
- **Never rename `publish.yml`.** PyPI's trusted publishing is bound to the workflow's filename.
- **Never bump a version in a work PR**, or release without KI7MT's go (security excepted).
- **Never put a branch filter on `ci.yml`'s `pull_request` trigger.** `main` is the only
  long-lived branch, so it looks redundant — and it is not. Narrowed to `branches: [main]`, a pull
  request into anything else runs **no ruff, no mypy and no pytest** and still reports green. That
  happened on the pull request that performed this very migration: CodeQL was its only check.

## A release is done when it's published everywhere

**A release is complete only when PyPI and the Official MCP Registry
both serve the new version** (KI7MT, 2026-09-28). A PyPI release alone is
half a release.

`publish.yml` runs on **`workflow_dispatch`** — a person pressing Run workflow — and enforces
that, in this order:

1. **`security`**: the **release gate** first, and it now opens with two checks the old trigger
   made unnecessary:
   - **the run is from `main`.** `workflow_dispatch` can be started from any branch; `push: [main]`
     could not. Locked by the `pypi` Environment, stated here so a refusal explains itself.
   - **`ci-all-green` passed on `GITHUB_SHA`.** Under the old trigger a green release PR stood in
     front of the merge that published. A button has nothing in front of it, and this job only
     ever ran `test_security.py` — nothing established that the commit under the button had passed
     ruff, mypy or the 3.10–3.13 matrix. Needs `checks: read`.

   Then the version: the **typed** version must equal `pyproject.toml`'s, and must be **new** —
   only a 404 from PyPI counts as "not published", and only `git ls-remote` exit 2 as "no such
   tag"; anything it cannot confirm stops the release (fails closed). `server.json` must match.
   The version is computed here **once** and every later job uses it. Then the security tests.

   The typed version reaches the shell through **`env:`**, never a `${{ }}` expansion inside
   `run:` — an expansion is substituted before the shell sees it, which makes the input script
   rather than data — and it must match a version shape before it is compared.
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

Copy it whole; change nothing but the security-test path if the repo's differs. From
`wspr-mcp` after the 2026-10-25 migration — nine repositories hold this file byte for byte,
which is how it was chosen as canonical rather than by picking one.

```yaml
name: Publish to PyPI

# A release happens on purpose, not as a side effect of merging (KI7MT, 2026-10-25).
#
# This used to fire on a push to `main`, which made "merge the release PR" the act of
# publishing — and that is what forced two pull requests per release: one to prepare the
# version, and a second to merge `develop` into `main` and ship it.
#
# Now `main` is the one working branch. Merging into it builds and tests and publishes
# nothing; a release is Actions -> Publish to PyPI -> Run workflow, with the version
# typed in. Typed, because it is a decision: it must match what the tree already says,
# and every gate below refuses anything it cannot confirm.
on:
  workflow_dispatch:
    inputs:
      version:
        description: "The version to publish, e.g. 0.2.1 — must match pyproject.toml"
        required: true
        type: string

concurrency:
  group: publish
  cancel-in-progress: false

permissions:
  contents: read

jobs:
  security:
    name: Security gates
    runs-on: ubuntu-latest
    permissions:
      contents: read
      checks: read
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - uses: actions/checkout@v4

      # workflow_dispatch offers a branch picker, so unlike the old push trigger this
      # workflow can be started from anywhere. The lock is the pypi Environment's
      # deployment branch rule (main only); this is the same rule stated where a failed
      # run can show it, because an Environment rule rejects the deployment with no
      # explanation of what was wrong.
      - name: This runs from main
        run: |
          if [ "$GITHUB_REF" != "refs/heads/main" ]; then
            echo "FAIL: a release is published from main only (this is $GITHUB_REF)"
            exit 1
          fi

      # Merging no longer publishes, so nothing else guarantees that what is about to
      # be released is the code CI passed on. Under the old trigger the release PR had
      # to be green before the merge that published it; this restores that property.
      - name: CI passed on the commit being published
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          PASSED="$(gh api \
            "repos/${GITHUB_REPOSITORY}/commits/${GITHUB_SHA}/check-runs?check_name=ci-all-green" \
            --jq '[.check_runs[] | select(.conclusion == "success")] | length')"
          if [ "${PASSED:-0}" -lt 1 ]; then
            echo "FAIL: ci-all-green has not passed on ${GITHUB_SHA}"
            exit 1
          fi
          echo "ci-all-green passed on ${GITHUB_SHA}"

      # A release publishes a version that is not out yet. PyPI publishes
      # pyproject's version and the Registry server.json's, so they must agree too.
      # Computed once; every later job uses this value (needs.security.outputs.version).
      # The gate fails closed: anything it cannot confirm stops the release.
      - name: The version is the one asked for, new, and consistent
        id: version
        env:
          # Through the environment rather than interpolated into the script: a
          # ${{ }} expansion inside run: is substituted before the shell sees it, so
          # the input would be script rather than data. Only a writer can dispatch
          # this, and the rule is still input validation on every supplied string.
          ASKED: ${{ inputs.version }}
        run: |
          VERSION="$(grep -m1 '^version' pyproject.toml | cut -d'"' -f2)"
          if ! printf '%s' "$ASKED" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+([a-z0-9.-]*)$'; then
            echo "FAIL: '$ASKED' is not a version"
            exit 1
          fi
          # Typed by the person releasing, so a slip names a version that is not here
          # rather than shipping whatever happens to be on main.
          if [ "$ASKED" != "$VERSION" ]; then
            echo "FAIL: asked to publish ${ASKED}, but this tree is ${VERSION}"
            exit 1
          fi
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
            200) echo "FAIL: ${PACKAGE} ${VERSION} is already on PyPI. Bump the version before releasing."; exit 1 ;;
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

      - name: Install test dependencies
        run: pip install pytest pip-audit

      - name: Run security test suite
        run: python -m pytest tests/test_security.py -v

      - name: Audit dependencies for vulnerabilities
        # Audits this package's declared dependencies, and can fail: a known CVE stops the release.
        # A finding with no fix yet is excepted only explicitly: --ignore-vuln ID, with a reason and date.
        run: pip-audit --strict --desc on .

      - name: Grep check — no subprocess/shell
        run: |
          if grep -rn 'subprocess\.\|os\.system\|shell=True' src/; then
            echo "FAIL: subprocess/shell found in source"
            exit 1
          fi

      - name: Grep check — no plaintext http://
        run: |
          # Tests the output rather than the pipeline's exit status, because the
          # output is what this gate is actually asking about: are there any
          # plaintext URLs. An exit status answers a different question and
          # answers it through whichever grep is on PATH.
          #
          # The earlier comment here blamed macOS /usr/bin/grep for exiting 0 on
          # empty input. Measured 2026-10-25, that is false: /usr/bin/grep exits
          # 1 when no line is selected, as POSIX requires and as GNU grep does.
          # The FAIL-on-a-clean-tree that prompted this form came from a
          # non-conforming grep shim in an agent's shell. The form is kept
          # because it is right for its own reason, not for that one.
          hits="$(grep -rn 'http://' src/ | grep -v 'localhost\|127\.0\.0\.1\|::1' || true)"
          if [ -n "$hits" ]; then
            echo "$hits"
            echo "FAIL: non-HTTPS URL found in source"
            exit 1
          fi

      - name: Grep check — no credential logging
        run: |
          if grep -rn -i 'print.*password\|print.*api_key\|logging.*password\|logging.*api_key' src/; then
            echo "FAIL: credential logging found in source"
            exit 1
          fi

  publish:
    name: Build and publish to PyPI
    needs: security
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write  # Required for trusted publishing (OIDC)
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

#### The one variant: repositories that check an owner's document

`cq-zones-mcp`, `darc-dok-mcp` and `itu-zones-mcp` answer from a list somebody else owns, so
they carry a `sources` job that fetches that owner's published document and tests our facts
against it. **Only those three**, and in them `publish` needs both:
`needs: [security, sources]` instead of `needs: security`.

It used to live in `ci.yml`, conditioned on a pull request into `main`, which under the old
flow meant *a release PR*. Now every pull request targets `main`, so leaving it there would
fetch the owner's page on every lockfile bump — wasteful, and against our own rule about
respecting the endpoints we call. Here it runs exactly when it used to: immediately before
anything is published. It is the gate that correctly stopped `cq-zones-mcp` 0.2.0 when CQ's
page had changed.

**Drop the condition when you move it.** Under `workflow_dispatch`, `if: github.event_name == 'pull_request'` is simply false, so the job skips — and a skipped
`needs` dependency skips `publish` too. The workflow would never publish at all. That was
caught by verification rather than review, in two repositories, on 2026-10-25.

```yaml
  # The owner's document, checked immediately before anything is published rather than
  # on every pull request. This lived in ci.yml, conditioned on a pull request into
  # `main`, which under the old flow meant "a release PR". Now every pull request
  # targets `main`, so leaving it there would fetch the owner's page on every lockfile
  # bump — wasteful, and against this project's own rule about respecting the endpoints
  # it calls. Here it runs exactly when it used to, and it is the gate that correctly
  # stopped cq-zones-mcp 0.2.0 when CQ's page had changed.
  sources:
    name: sources (pre-release, our facts against the owner's document)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - uses: astral-sh/setup-uv@v6
        with:
          python-version: "3.12"
          enable-cache: true

      - name: Install (locked)
        run: uv sync --group dev --frozen

      - name: Download the sources (owner's documents, checked against their SHA-256)
        run: uv run python scripts/fetch_published.py

      - name: Tests against the sources (AD1C and ARRL fetched by the tests)
        run: uv run pytest tests --live --ignore=tests/test_security.py -v
```

### Migrating a repo, and the trap in the middle

The `Release PR source` job is **retired**. It existed only to police which branch could open a
pull request into `main`, which stopped meaning anything once `main` became the working branch.

Its removal cannot be done in any order you like, because `main` *required that check*. Delete
the job and merge, and `main` sits behind a required status check that nothing produces any more:
every later pull request waits forever, including the one that would fix it. The sequence, per
repository:

1. **`pypi` Environment → Deployment branches → `main` only.** First, because it is the lock.
2. **Merge the workflow change.**
3. **Change the ruleset**: require **`ci-all-green`** in place of `Release PR source`. Not
   *nothing* — otherwise `main` requires no CI at all.
4. **Reach `main`** (under the old flow, one last `develop` → `main` merge). **Publishes nothing**:
   the merge commit carries the new `publish.yml`, so there is no push trigger left to fire.
5. **Then the cleanup**: default branch → `main`, drop `develop` from the protecting ruleset,
   delete `develop`.

Step 3 cannot move in either direction. Before step 2 the ruleset still demands a check `ci.yml`
no longer produces, so nothing merges at all. Left until after step 4, it is the same deadlock one
merge later.

`ci.yml` and any other CI workflow run on `push` to `main`, and on **every** pull request
whatever its base — see *Never*, above, for why that trigger carries no branch filter.

---

## Registry-publish job

**Purpose**: after a successful PyPI publish (the release run, started from Actions on `main`), publish the same version to the [Official MCP Registry](https://registry.modelcontextprotocol.io)
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
  after each PyPI publish, using GitHub OIDC for auth. Runs as part of the
  release workflow; no manual steps. Pattern documented in
  [qso-graph/.github/TEMPLATES.md](https://github.com/qso-graph/.github/blob/main/TEMPLATES.md).
- **Registry version badge** in README — PyPI and Registry versions
  are visible side-by-side so any drift between publishing surfaces
  is immediately apparent.
- **Release gates** — `server.json` must agree with `pyproject.toml`, the
  version must be absent from PyPI and untagged, and a `verify` job fails
  the release unless PyPI and the MCP Registry both serve the new version
  before the tag is cut.
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

The whole file, from `wspr-mcp` after the migration.

```yaml
name: CI

# A pull request is tested whatever it targets, and deliberately has no branch
# filter. `main` is the one long-lived branch now, so `push` names it; but a filter
# here would mean a pull request into any other branch ran no ruff, no mypy and no
# pytest while still reporting green. That is not hypothetical: narrowing this to
# [main] is what let the pull request making this very change merge with CodeQL as
# its only check.
on:
  pull_request:
  push:
    branches: [main]

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  # Lint and types, once rather than per Python: both read the source, and
  # neither answer changes with the interpreter running them (qso-graph-devel#66).
  lint:
    name: ruff and mypy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - uses: astral-sh/setup-uv@v6
        with:
          python-version: "3.11"
          enable-cache: true

      - name: Install (locked)
        run: uv sync --group dev --frozen

      - name: Lint (ruff)
        run: uv run ruff check .

      - name: Type-check (mypy)
        run: uv run mypy src

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

  ci-all-green:
    name: ci-all-green
    needs: [lint, test]
    runs-on: ubuntu-latest
    if: always()
    steps:
      - name: Verify required jobs all succeeded
        run: |
          if [[ "${{ needs.lint.result }}" != "success" ]]; then
            echo "FAIL: ruff or mypy did not pass (result=${{ needs.lint.result }})"
            exit 1
          fi
          if [[ "${{ needs.test.result }}" != "success" ]]; then
            echo "FAIL: test matrix did not all succeed (result=${{ needs.test.result }})"
            exit 1
          fi
          echo "All required CI jobs passed."
```

`--frozen` fails CI if `uv.lock` is out of date with `pyproject.toml`, so the lock can't drift.
Repos that also test Windows or macOS keep their `os` matrix.

---

## MCP protocol conformance

A qso-graph MCP server must be valid against the **Model Context Protocol specification**, not only
against our own conventions. This file describes how to *publish* a server in detail; these are the
things that make one *valid*, measured against revision `2026-07-28`.

**Tool errors set `isError`.** A tool execution error — bad input, upstream failure, business-logic
refusal — is reported in the result with `isError: true`. Returning `{"error": "..."}` as a successful
result hides the failure from the model, and the spec says so directly: otherwise "the LLM would not be
able to see that an error occurred and self-correct". Raise `ToolError` and FastMCP sets the flag.
Errors in *finding* a tool stay JSON-RPC protocol errors.

**Every tool declares its annotation hints**, because the defaults are pessimistic:

| Field | Default when omitted |
|---|---|
| `readOnlyHint` | false |
| `destructiveHint` | **true** |
| `idempotentHint` | false |
| `openWorldHint` | **true** |

A read-only tool that declares nothing is advertised as potentially destructive and open-world, and a
client is then entitled to put a confirmation prompt in front of it. `openWorldHint` is the one that
varies per tool: true where it reads a live external service, false where it answers from carried data.
Annotations are a client UX hint and **never a security control** — the spec requires clients to treat
them as untrusted.

**Protocol revision currency is a dependency decision**, tracked once for the fleet. Do not hand-roll
protocol features the installed `fastmcp`/`mcp` does not implement.

See `qso-graph-devel/planning/MCP-SECURITY-FRAMEWORK.md` for the full section, and the specification at
https://modelcontextprotocol.io/specification/latest.

---

## Rollout checklist (per repo)

In this order. Settings first, so nothing can be deleted or squashed while the rest changes.

- [ ] **Ruleset protecting `main`**: deletion, non-fast-forward, and **pull request required**
      (0 approvals)
- [ ] **Merge commits only** (squash and rebase off)
- [ ] **`main` is the default branch**, and the only long-lived one
- [ ] **`pypi` Environment → Deployment branches → Selected → `main`**
- [ ] One PR into `main`: the canonical **`publish.yml`** and **`ci.yml`** — `publish.yml` on
      `workflow_dispatch` only, `ci.yml` with **no branch filter on `pull_request`**
- [ ] `main` requires the `ci-all-green` check (after that PR has run once, so the check exists)
- [ ] `server.json` at repo root, `name` `io.github.qso-graph/<repo-name>`, `packages[0]`
      `registryType: pypi`, `identifier` = the PyPI name; `mcp-publisher validate` passes
- [ ] `CHANGELOG.md` has `## [Unreleased]` at the top
- [ ] README has the PyPI and MCP Registry badges
- [ ] **uv**: `[dependency-groups] dev`, `uv.lock` committed, `ci.yml` on `setup-uv` with
      `uv sync --group dev --frozen`; README uses `uvx` and `uv sync` / `uv run pytest`
- [ ] **MCP protocol conformance** (revision `2026-07-28`):
      tool execution errors raise `ToolError` so the result carries `isError: true`;
      every tool declares `readOnlyHint`, `destructiveHint`, `idempotentHint` and
      `openWorldHint`; a test asserts both
- [ ] **TLS**: outbound HTTPS over stdlib `urllib` uses a `certifi` root set, and a test
      asserts `CERT_REQUIRED` and `check_hostname` — verification is never disabled
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
