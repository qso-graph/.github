# QSO Graph — Open-Source Software for Amateur Radio

[![Live Demo](https://img.shields.io/badge/demo-live-22c55e?style=flat-square&logo=github)](https://qso-graph.io/qso-graph-demo-logbook/)
[![DXpedition Demo](https://img.shields.io/badge/DXpeditions-3Y0K_Bouvet-f59e0b?style=flat-square&logo=github)](https://qso-graph.io/qso-graph-demo-dxpedition/)
[![Docs](https://img.shields.io/badge/docs-qso--graph.io-3b82f6?style=flat-square)](https://qso-graph.io)

**Open amateur radio software, built to work together.**

QSO Graph is open amateur radio software for your station: logging, nets, awards, spots and your radio, in one place, on Windows, macOS and Linux, with the libraries and AI integrations behind them. **Today** that is the MCP servers and the libraries under them; **QSO Graph Desktop**, the app that brings it together, is released: 0.4.0 is the Stable release on Windows, Linux and macOS. They share one data model, publish their interfaces, and are built so that any of them can be used alone. Free software under the GPL, for individual operators and for clubs, small and large.

**[View the live demo →](https://qso-graph.io/qso-graph-demo-logbook/)** · **[Documentation →](https://qso-graph.io)**

## Today

- **[MCP servers](#mcp-servers)** that connect AI assistants to the services hams use every day: QRZ, LoTW, eQSL, HamQTH, POTA, SOTA, IOTA, NOAA space weather, WSPR, OMISS, NetLogger, N1MM Logger+, IONIS-AI propagation analytics, and the ADIF specification itself. Published on PyPI; each one runs with a single `uvx` command, nothing to install.
- **[Tools](#packages)** that look after them: credential handling that keeps your passwords in your operating system's keyring, and a relay that gives local LLMs the same tools.
- **[Live demos](#demos)** of what that makes possible: logbook analysis, and DXpedition propagation planning.

## Where we're heading

| Product | What it is | Status |
|:--------|:-----------|:-------|
| **[QSO Graph Desktop](https://github.com/qso-graph/qso-graph-desktop)** | A desktop home for your station on Windows, Linux and macOS: your callsigns and their logins (kept in your own OS credential store), your Locations, Parks On the Air, band conditions, the sun and moon, and ADIF Lookup, each an extension. Integrations with WSJT-X and the programs you already run come next. Signed downloads, a signed apt/dnf repository, and Homebrew | **Available** ([0.4.0](https://github.com/qso-graph/qso-graph-desktop/releases/latest)), growing milestone by milestone |
| **[QSO Graph SDK](https://github.com/qso-graph/qso-graph-sdk)** (QGSDK) | The build kit: pick what you work on (QSO Graph Desktop, the Qt logger or the MCP servers) and get exactly its tools, pinned, with one command on Windows, Linux or macOS, so anyone can build them | **Available** ([latest](https://github.com/qso-graph/qso-graph-sdk/releases/latest)) |

Earlier plans for a separate net logger, an ADIF service and a self-hosted club server are folded into QSO Graph Desktop.

For developers: [qso-graph-sim](https://github.com/qso-graph/qso-graph-sim) replays a program's network messages from its own log (WSJT-X first), so integrations can be tested without a radio, and the [Homebrew tap](https://github.com/qso-graph/homebrew-tap) carries QSO Graph Desktop's Stable releases for macOS.

Products are linked here as each becomes public.

**In order:**

1. **Now: one app for the station, built properly.** QSO Graph Desktop, to enterprise security standards; 0.4.0 is the Stable release.
2. **With it: the clubs with nothing.** Club rosters, nets and awards for the many clubs and nets that have no software or server of their own.
3. **Then: publish the seams.** The interfaces between the pieces become published specifications that anyone can implement, including software that isn't ours.
4. **Eventually: governance that isn't us.** Clubs, small and large with an equal voice, steering the parts that affect them, through the specifications.

Underneath all of it, continuously: the data. ADIF as the base, propagation as the research edge.

**How the pieces fit:**

- **[ADIF](https://adif.org/) is the base.** Every QSO Graph tool reads and writes ADIF, the format LoTW, eQSL, QRZ and every major logger share, and uses ADIF's own definition for every field ADIF defines. **No one-off custom fields:** when a tool genuinely needs something ADIF doesn't have, it is defined **once**, published, and used the same way across every QSO Graph tool where it applies. That costs more than a quick private field, and it's a cost accepted deliberately: it's what keeps the tools working together, and what lets you take your log anywhere.
- **Shared contracts, not shared code.** The pieces talk through published APIs and the same reference data (ADIF, DXCC), and are tested against the same recorded service responses, so a Python MCP server and the desktop app agree on what a service means.
- **Each piece stands alone.** Every service is a library with thin layers over it: an MCP server for AI assistants, and the desktop app's own screens. Each works on its own; club features connect when a club has them.

**What we don't do:** replace LoTW, eQSL or QRZ. QSO Graph records, queries and predicts contacts, and connects to those services rather than standing in for them.

## MCP Servers

The integration layer, available now. Open-source [Model Context Protocol](https://modelcontextprotocol.io) servers that connect AI assistants to amateur radio services. Ask Claude, ChatGPT, Copilot, or Gemini about your QSOs, confirmations, and logbook data — no manual API wrangling required.

**Nothing to install per server.** Every server, its tools and its current version: [qso-graph.io](https://qso-graph.io).

### Install

Install [uv](https://docs.astral.sh/uv/) once:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh                  # Linux / macOS
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"      # Windows
```

Then your MCP client runs each server with `uvx`, always the current release:

```json
"command": "uvx", "args": ["solar-mcp"]
```

Command-line tools install with `uv tool install`: `qso-graph-auth` (credentials, the `qso-auth` command) and `qsp-client` (the local-LLM relay). Client configs for Claude Desktop, Claude Code, ChatGPT, Cursor, VS Code and Gemini CLI: [Getting Started](https://qso-graph.io/getting-started/).

### Security — Our #1 Priority

**Your credentials never leave the OS keyring.** Every qso-graph server enforces non-negotiable security guarantees:

- Credentials stored in OS keyring only (macOS Keychain, Windows Credential Manager, Linux Secret Service) — never in config files, environment variables, or logs
- Credentials never appear in MCP tool results, error messages, or debug output — enforced by architecture, not policy
- No command injection surface — no `subprocess`, no `shell=True`, no `eval`
- All external connections HTTPS only
- Every server that calls an outside service respects that service's request limits, and
  treats a `429` as the limit it is: it waits the interval the service asks for rather than
  retrying into it
- A security gate every PyPI release must pass before the upload runs: the security test
  suite, a dependency audit against known advisories, and source checks for credential
  logging, plaintext `http://` and subprocess use. It is mechanical, not a review — nothing
  ships past a red gate, and no human sign-off is claimed in its place

Full details: [Security](https://qso-graph.io/security/)

### Packages

#### Foundation

| Package | Purpose | Status |
|:--------|:--------|:-------|
| [adif-mcp](https://github.com/qso-graph/adif-mcp) | ADIF 3.1.7 spec parsing, validation, enumerations (8 tools) | [![PyPI](https://img.shields.io/pypi/v/adif-mcp?label=PyPI&color=blue)](https://pypi.org/project/adif-mcp/) |
| [qso-graph-auth](https://github.com/qso-graph/qso-graph-auth) | Persona management, OS keyring credentials, `qso-auth` CLI | [![PyPI](https://img.shields.io/pypi/v/qso-graph-auth?label=PyPI&color=blue)](https://pypi.org/project/qso-graph-auth/) |

#### Logbook Services (Authenticated)

| Package | Service | Tools | Status |
|:--------|:--------|:------|:-------|
| [eqsl-mcp](https://github.com/qso-graph/eqsl-mcp) | [eQSL.cc](https://www.eqsl.cc/) | 6 tools: inbox, verify, AG status, download, last upload, version info | [![PyPI](https://img.shields.io/pypi/v/eqsl-mcp?label=PyPI&color=blue)](https://pypi.org/project/eqsl-mcp/) |
| [lotw-mcp](https://github.com/qso-graph/lotw-mcp) | [LoTW](https://lotw.arrl.org/) | 6 tools: confirmations, QSOs, DXCC credits, download, user activity, version info | [![PyPI](https://img.shields.io/pypi/v/lotw-mcp?label=PyPI&color=blue)](https://pypi.org/project/lotw-mcp/) |
| [qrz-mcp](https://github.com/qso-graph/qrz-mcp) | [QRZ.com](https://www.qrz.com/) | 6 tools: lookup, DXCC, logbook status, download, logbook fetch, version info | [![PyPI](https://img.shields.io/pypi/v/qrz-mcp?label=PyPI&color=blue)](https://pypi.org/project/qrz-mcp/) |
| [hamqth-mcp](https://github.com/qso-graph/hamqth-mcp) | [HamQTH](https://www.hamqth.com/) | 8 tools: lookup, DXCC, bio, activity, DX spots, RBN, verify QSO, version info | [![PyPI](https://img.shields.io/pypi/v/hamqth-mcp?label=PyPI&color=blue)](https://pypi.org/project/hamqth-mcp/) |

#### Public Services (No Auth Required)

| Package | Service | Tools | Status |
|:--------|:--------|:------|:-------|
| [pota-mcp](https://github.com/qso-graph/pota-mcp) | [POTA](https://pota.app/) | 11 tools: spots, park info, stats, activations, leaderboard, schedules, location, nearby, rare parks nearby, activator, version info | [![PyPI](https://img.shields.io/pypi/v/pota-mcp?label=PyPI&color=blue)](https://pypi.org/project/pota-mcp/) |
| [sota-mcp](https://github.com/qso-graph/sota-mcp) | [SOTA](https://www.sota.org.uk/) | 5 tools: spots, alerts, summit info, nearby summits, version info | [![PyPI](https://img.shields.io/pypi/v/sota-mcp?label=PyPI&color=blue)](https://pypi.org/project/sota-mcp/) |
| [iota-mcp](https://github.com/qso-graph/iota-mcp) | [IOTA](https://www.iota-world.org/) | 7 tools: group lookup, island search, DXCC mapping, nearby, stats, version info | [![PyPI](https://img.shields.io/pypi/v/iota-mcp?label=PyPI&color=blue)](https://pypi.org/project/iota-mcp/) |
| [solar-mcp](https://github.com/qso-graph/solar-mcp) | [NOAA SWPC](https://www.swpc.noaa.gov/) | 7 tools: SFI, Kp, solar wind, X-ray flux, band outlook, alerts, version info | [![PyPI](https://img.shields.io/pypi/v/solar-mcp?label=PyPI&color=blue)](https://pypi.org/project/solar-mcp/) |
| [wspr-mcp](https://github.com/qso-graph/wspr-mcp) | [WSPR](https://www.wsprnet.org/) | 9 tools: spots, band activity, top beacons/spotters, propagation, grid, SNR, version info | [![PyPI](https://img.shields.io/pypi/v/wspr-mcp?label=PyPI&color=blue)](https://pypi.org/project/wspr-mcp/) |
| [ionis-mcp](https://github.com/qso-graph/ionis-mcp) | [IONIS-AI](https://github.com/IONIS-AI) | 12 tools: HF propagation analytics from 175M+ signatures (14B observations) | [![PyPI](https://img.shields.io/pypi/v/ionis-mcp?label=PyPI&color=blue)](https://pypi.org/project/ionis-mcp/) |
| [eme-mcp](https://github.com/qso-graph/eme-mcp) | moonbounce (computed locally) | 5 tools: moon window, path loss, degradation, calendar, version info | [![PyPI](https://img.shields.io/pypi/v/eme-mcp?label=PyPI&color=blue&cacheSeconds=3600)](https://pypi.org/project/eme-mcp/) |
| [meteor-mcp](https://github.com/qso-graph/meteor-mcp) | [Global Meteor Network](https://globalmeteornetwork.org/) + NASA CNEOS | 7 tools: best windows, showers, shower info, activity, fireballs, source info, version info | [![PyPI](https://img.shields.io/pypi/v/meteor-mcp?label=PyPI&color=blue&cacheSeconds=3600)](https://pypi.org/project/meteor-mcp/) |
| [omiss-mcp](https://github.com/qso-graph/omiss-mcp) | [OMISS](https://www.omiss.net/) | 14 tools: net schedule, nets on the air, member lookup, check-in history, past net check-ins, Statehood, officers, awards, award rules, award recipients, award eligibility, net statistics, set callsign, version info | [![PyPI](https://img.shields.io/pypi/v/omiss-mcp?label=PyPI&color=blue&cacheSeconds=3600)](https://pypi.org/project/omiss-mcp/) |

#### Reference Data (No Auth, No Network)

The lists ADIF's fields point to but ADIF doesn't define, each as its owner publishes it, credited to the owner. The facts ship with the package; the owner's document doesn't.

| Package | Owner's list | Tools | Status |
|:--------|:-------------|:------|:-------|
| [cq-zones-mcp](https://github.com/qso-graph/cq-zones-mcp) | CQ zones: [CQ's WAZ Zone Definitions](https://cqww.com/cq_waz_list.htm) (CQ / WWROF) | 6 tools: lookup, codes for an entity, search, valid on a date, source info, version info | [![PyPI](https://img.shields.io/pypi/v/cq-zones-mcp?label=PyPI&color=blue&cacheSeconds=3600)](https://pypi.org/project/cq-zones-mcp/) |
| [itu-zones-mcp](https://github.com/qso-graph/itu-zones-mcp) | ITU zones: [IARU HF Managers Handbook, ch. 9.8](https://www.iaru-r1.org/wp-content/uploads/2019/12/IARURegion1HFManagerHandbook8.2.1.pdf) (IARU Region 1) | 6 tools: lookup, codes for an entity, search, valid on a date, source info, version info | [![PyPI](https://img.shields.io/pypi/v/itu-zones-mcp?label=PyPI&color=blue&cacheSeconds=3600)](https://pypi.org/project/itu-zones-mcp/) |
| [darc-dok-mcp](https://github.com/qso-graph/darc-dok-mcp) | DOKs and special DOKs: [DARC](https://www.darc.de/)'s DOK-Liste and special-DOK list | 6 tools: lookup, valid on a date, search, codes for an entity, source info, version info | [![PyPI](https://img.shields.io/pypi/v/darc-dok-mcp?label=PyPI&color=blue&cacheSeconds=3600)](https://pypi.org/project/darc-dok-mcp/) |

#### Published, not yet working

On PyPI so the name is reserved and the release machinery is proven, and each
answers `get_version_info` with *"in development — no working tools yet"*. They
are listed here so that is said rather than discovered: installing one today
gets you a version number and nothing else.

| Package | Planned | Status |
|:--------|:--------|:-------|
| [dxe-mcp](https://github.com/qso-graph/dxe-mcp) | DXpedition tracking | In development — no working tools |
| [js8call-mcp](https://github.com/qso-graph/js8call-mcp) | JS8Call HF messaging | In development — no working tools |
| [qso-graph-contest-mcp](https://github.com/qso-graph/qso-graph-contest-mcp) | Contest calendar and rules | In development — no working tools |

#### Radio Logging

| Package | Service | Tools | Status |
|:--------|:--------|:------|:-------|
| [n1mm-mcp](https://github.com/qso-graph/n1mm-mcp) | [N1MM Logger+](https://n1mm.hamdocs.com/) | 12 tools: station state, lookup, contacts, bandmap, performance, multipliers, clock, network, pileup, SO2R, diagnostics, version info | [![PyPI](https://img.shields.io/pypi/v/n1mm-mcp?label=PyPI&color=blue)](https://pypi.org/project/n1mm-mcp/) |
| [netlogger-mcp](https://github.com/qso-graph/netlogger-mcp) | [NetLogger](https://www.netlogger.org/) | 6 tools: active nets, live check-ins and who's up, past nets, past check-ins, set callsign, version info | [![PyPI](https://img.shields.io/pypi/v/netlogger-mcp?label=PyPI&color=blue)](https://pypi.org/project/netlogger-mcp/) |

#### Infrastructure

| Package | Purpose | Status |
|:--------|:--------|:-------|
| [qsp-client](https://github.com/qso-graph/qsp-client) | QSP — an MCP client that relays tools to any local LLM (llama.cpp, Ollama, vLLM, SGLang). Formerly qsp-mcp | [![PyPI](https://img.shields.io/pypi/v/qsp-client?label=PyPI&color=blue)](https://pypi.org/project/qsp-client/) |

## Demos

| Demo | Description | Status |
|:-----|:------------|:-------|
| [qso-graph-demo-logbook](https://github.com/qso-graph/qso-graph-demo-logbook) | QSO logbook analysis showcase (Next.js, GitHub Pages) | [Live Demo](https://qso-graph.io/qso-graph-demo-logbook/) |
| [qso-graph-demo-dxpedition](https://github.com/qso-graph/qso-graph-demo-dxpedition) | DXpedition propagation analysis — 3Y0K Bouvet Island (Next.js, GitHub Pages) | [Live Demo](https://qso-graph.io/qso-graph-demo-dxpedition/) |

## Related Projects

| Project | Description |
|:--------|:------------|
| [ionis-jupyter](https://github.com/IONIS-AI/ionis-jupyter) | Jupyter notebooks for propagation research |

## Quick Start

```bash
# Install uv once (Linux / macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run any server
uvx solar-mcp

# Credentials for the logbook servers
uv tool install qso-graph-auth
```

Each server works with any MCP client: Claude Desktop, Claude Code, ChatGPT, Cursor, VS Code / GitHub Copilot, Windsurf, Gemini CLI, Goose, and Codex CLI — or use [qsp-client](https://github.com/qso-graph/qsp-client) to relay tools to any local LLM.

## Architecture

```
qso-graph-auth (identity)       MCP Servers (qso-graph)
 ├── PersonaManager        ──>   eqsl-mcp, qrz-mcp, lotw-mcp, hamqth-mcp
 ├── OS keyring credentials      Each server = 1 uvx
 └── qso-auth CLI                Each server = 5-14 MCP tools

adif-mcp (ADIF spec)            Public Servers
 └── 8 spec tools          ──>   solar, pota, sota, iota, wspr, omiss,
                                 ionis, netlogger (no auth); n1mm (local)

qsp-client (tool relay)         Local LLM Inference
 └── Stateless pipe        ──>   llama.cpp, Ollama, vLLM, SGLang
     MCP tools → OpenAI           Any model with function calling
     tools format                  Zero cloud dependency
```

## Reporting Security Issues

Do NOT open public GitHub issues for security vulnerabilities. Email: maintainers@qso-graph.io with subject `[SECURITY] qso-graph vulnerability report`.

## License

GPL-3.0-or-later
