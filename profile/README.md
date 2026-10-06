# QSO Graph — Open-Source Software for Amateur Radio

[![Live Demo](https://img.shields.io/badge/demo-live-22c55e?style=flat-square&logo=vercel)](https://qso-graph-demo.vercel.app/)
[![DXpedition Demo](https://img.shields.io/badge/DXpeditions-3Y0K_Bouvet-f59e0b?style=flat-square&logo=vercel)](https://dxpedition-demo.vercel.app/)
[![Docs](https://img.shields.io/badge/docs-qso--graph.io-3b82f6?style=flat-square)](https://qso-graph.io)

**Open amateur radio software, built to work together.**

QSO Graph is open amateur radio software for your station: logging, nets, awards, spots and your radio, in one place, on Windows, macOS and Linux, with the libraries and AI integrations behind them. **Today** that is the MCP servers and the libraries under them; **QSO Graph Desktop**, the app that brings it together, is in design. They share one data model, publish their interfaces, and are built so that any of them can be used alone. Free software under the GPL, for individual operators and for clubs, small and large.

**[View the live demo →](https://qso-graph-demo.vercel.app/)** · **[Documentation →](https://qso-graph.io)**

## Today

- **[MCP servers](#mcp-servers)** that connect AI assistants to the services hams use every day: QRZ, LoTW, eQSL, HamQTH, POTA, SOTA, IOTA, NOAA space weather, WSPR, OMISS, NetLogger, N1MM Logger+, IONIS-AI propagation analytics, and the ADIF specification itself. Published on PyPI; each one runs with a single `uvx` command, nothing to install.
- **[Tools](#packages)** that look after them: credential handling that keeps your passwords in your operating system's keyring, and a relay that gives local LLMs the same tools.
- **[Live demos](#demos)** of what that makes possible: logbook analysis, and DXpedition propagation planning.

## Where we're heading

| Product | What it is | Status |
|:--------|:-----------|:-------|
| **QSO Graph Desktop** | One app for your station on Windows, macOS and Linux: your logbook, nets, awards, spots and your radio, with your callsigns and logins kept in your own OS keyring | In design |
| **[QSO Graph SDK](https://github.com/qso-graph/qso-graph-sdk)** (QGSDK) | The build kit for QSO Graph's standalone apps: Qt and CMake, one command to a pinned build environment on Windows or Linux, so anyone can build them | **Available** (open source) |

Earlier plans for a separate net logger, an ADIF service and a self-hosted club server are folded into it.

Products are linked here as each becomes public.

**In order:**

1. **Now: one app for the station, designed properly.** QSO Graph Desktop, built to enterprise security standards.
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
- Rate limiting on every API to prevent account bans
- Independent security audit required before every PyPI release

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
| [pota-mcp](https://github.com/qso-graph/pota-mcp) | [POTA](https://pota.app/) | 8 tools: spots, park info, stats, schedules, location, nearby, activator, version info | [![PyPI](https://img.shields.io/pypi/v/pota-mcp?label=PyPI&color=blue)](https://pypi.org/project/pota-mcp/) |
| [sota-mcp](https://github.com/qso-graph/sota-mcp) | [SOTA](https://www.sota.org.uk/) | 5 tools: spots, alerts, summit info, nearby summits, version info | [![PyPI](https://img.shields.io/pypi/v/sota-mcp?label=PyPI&color=blue)](https://pypi.org/project/sota-mcp/) |
| [iota-mcp](https://github.com/qso-graph/iota-mcp) | [IOTA](https://www.iota-world.org/) | 7 tools: group lookup, island search, DXCC mapping, nearby, stats, version info | [![PyPI](https://img.shields.io/pypi/v/iota-mcp?label=PyPI&color=blue)](https://pypi.org/project/iota-mcp/) |
| [solar-mcp](https://github.com/qso-graph/solar-mcp) | [NOAA SWPC](https://www.swpc.noaa.gov/) | 7 tools: SFI, Kp, solar wind, X-ray flux, band outlook, alerts, version info | [![PyPI](https://img.shields.io/pypi/v/solar-mcp?label=PyPI&color=blue)](https://pypi.org/project/solar-mcp/) |
| [wspr-mcp](https://github.com/qso-graph/wspr-mcp) | [WSPR](https://www.wsprnet.org/) | 9 tools: spots, band activity, top beacons/spotters, propagation, grid, SNR, version info | [![PyPI](https://img.shields.io/pypi/v/wspr-mcp?label=PyPI&color=blue)](https://pypi.org/project/wspr-mcp/) |
| [ionis-mcp](https://github.com/qso-graph/ionis-mcp) | [IONIS-AI](https://github.com/IONIS-AI) | 12 tools: HF propagation analytics from 175M+ signatures (14B observations) | [![PyPI](https://img.shields.io/pypi/v/ionis-mcp?label=PyPI&color=blue)](https://pypi.org/project/ionis-mcp/) |
| [omiss-mcp](https://github.com/qso-graph/omiss-mcp) | [OMISS](https://www.omiss.net/) | 13 tools: net schedule, nets on the air, member lookup, check-in history, past net check-ins, Statehood, officers, awards, award rules, award recipients, net statistics, set callsign, version info | [![PyPI](https://img.shields.io/pypi/v/omiss-mcp?label=PyPI&color=blue&cacheSeconds=3600)](https://pypi.org/project/omiss-mcp/) |

#### Radio Logging

| Package | Service | Tools | Status |
|:--------|:--------|:------|:-------|
| [n1mm-mcp](https://github.com/qso-graph/n1mm-mcp) | [N1MM Logger+](https://n1mm.hamdocs.com/) | 9 tools: station state, lookup, contacts, bandmap, performance, multipliers, clock, diagnostics, version info | [![PyPI](https://img.shields.io/pypi/v/n1mm-mcp?label=PyPI&color=blue)](https://pypi.org/project/n1mm-mcp/) |
| [netlogger-mcp](https://github.com/qso-graph/netlogger-mcp) | [NetLogger](https://www.netlogger.org/) | 6 tools: active nets, live check-ins and who's up, past nets, past check-ins, set callsign, version info | [![PyPI](https://img.shields.io/pypi/v/netlogger-mcp?label=PyPI&color=blue)](https://pypi.org/project/netlogger-mcp/) |

#### Infrastructure

| Package | Purpose | Status |
|:--------|:--------|:-------|
| [qsp-client](https://github.com/qso-graph/qsp-client) | QSP — an MCP client that relays tools to any local LLM (llama.cpp, Ollama, vLLM, SGLang). Formerly qsp-mcp | [![PyPI](https://img.shields.io/pypi/v/qsp-client?label=PyPI&color=blue)](https://pypi.org/project/qsp-client/) |

### Quick Start

```bash
# Install uv once (Linux / macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run any server
uvx solar-mcp

# Credentials for the logbook servers
uv tool install qso-graph-auth
```

Each server works with any MCP client: Claude Desktop, Claude Code, ChatGPT, Cursor, VS Code / GitHub Copilot, Windsurf, Gemini CLI, Goose, and Codex CLI — or use [qsp-client](https://github.com/qso-graph/qsp-client) to relay tools to any local LLM.

### Architecture

```
qso-graph-auth (identity)       MCP Servers (qso-graph)
 ├── PersonaManager        ──>   eqsl-mcp, qrz-mcp, lotw-mcp, hamqth-mcp
 ├── OS keyring credentials      Each server = 1 uvx
 └── qso-auth CLI                Each server = 5-13 MCP tools

adif-mcp (ADIF spec)            Public Servers
 └── 8 spec tools          ──>   solar, pota, sota, iota, wspr, omiss,
                                 ionis, netlogger (no auth); n1mm (local)

qsp-client (tool relay)         Local LLM Inference
 └── Stateless pipe        ──>   llama.cpp, Ollama, vLLM, SGLang
     MCP tools → OpenAI           Any model with function calling
     tools format                  Zero cloud dependency
```

## Demos

| Demo | Description | Status |
|:-----|:------------|:-------|
| [qso-graph-demo](https://github.com/qso-graph/qso-graph-demo) | QSO logbook analysis showcase (Next.js / Vercel) | [Live Demo](https://qso-graph-demo.vercel.app/) |
| [dxpedition-demo](https://github.com/qso-graph/dxpedition-demo) | DXpedition propagation analysis — 3Y0K Bouvet Island (Next.js / Vercel) | [Live Demo](https://dxpedition-demo.vercel.app/) |

## Related Projects

| Project | Description |
|:--------|:------------|
| [ionis-jupyter](https://github.com/IONIS-AI/ionis-jupyter) | Jupyter notebooks for propagation research |

## Reporting Security Issues

Do NOT open public GitHub issues for security vulnerabilities. Email: ki7mt@yahoo.com with subject `[SECURITY] qso-graph vulnerability report`.

## License

GPL-3.0-or-later
