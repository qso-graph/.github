# QSO-Graph — MCP Servers for Amateur Radio

[![Live Demo](https://img.shields.io/badge/demo-live-22c55e?style=flat-square&logo=vercel)](https://qso-graph-demo.vercel.app/)
[![DXpedition Demo](https://img.shields.io/badge/DXpeditions-3Y0K_Bouvet-f59e0b?style=flat-square&logo=vercel)](https://dxpedition-demo.vercel.app/)
[![Docs](https://img.shields.io/badge/docs-qso--graph.io-3b82f6?style=flat-square)](https://qso-graph.io)

Open-source [Model Context Protocol](https://modelcontextprotocol.io) servers that connect AI assistants to amateur radio services. Ask Claude, ChatGPT, Copilot, or Gemini about your QSOs, confirmations, and logbook data — no manual API wrangling required.

**One install command.** Every server, its tools and its current version: [qso-graph.io](https://qso-graph.io).

**[View the live demo →](https://qso-graph-demo.vercel.app/)** · **[Documentation →](https://qso-graph.io)**

## Install

```bash
curl -sL https://qso-graph.io/install.sh | bash
```

Creates `~/.qso-graph/` with an isolated Python environment, installs the
base MCP servers, and adds them to your PATH. Works
on Linux and macOS. No root required.

After install, run `qso-graph-config` to manage servers, credentials,
datasets, and MCP client configuration via an interactive TUI.

**Advanced users** can run any server directly with [uv](https://docs.astral.sh/uv/), nothing to install: `uvx solar-mcp`, and `"command": "uvx", "args": ["solar-mcp"]` in your MCP client. Or install the bundles with pip:

```bash
pip install qso-graph-config                    # Base servers
pip install "qso-graph-config[auth]"            # + 4 logbook servers
pip install "qso-graph-config[ionis]"           # + ionis-mcp propagation
pip install "qso-graph-config[full]"            # Everything
```

## Security — Our #1 Priority

**Your credentials never leave the OS keyring.** Every qso-graph server enforces non-negotiable security guarantees:

- Credentials stored in OS keyring only (macOS Keychain, Windows Credential Manager, Linux Secret Service) — never in config files, environment variables, or logs
- Credentials never appear in MCP tool results, error messages, or debug output — enforced by architecture, not policy
- No command injection surface — no `subprocess`, no `shell=True`, no `eval`
- All external connections HTTPS only
- Rate limiting on every API to prevent account bans
- Independent security audit required before every PyPI release

Full details: [Security](https://qso-graph.io/security/)

## Packages

### Installer

| Package | Purpose | Status |
|:--------|:--------|:-------|
| [qso-graph-config](https://github.com/qso-graph/qso-graph-config) | Installer and manager — TUI, upgrades, config generation, dataset downloads | [![PyPI](https://img.shields.io/pypi/v/qso-graph-config?label=PyPI&color=blue)](https://pypi.org/project/qso-graph-config/) |

### Foundation

| Package | Purpose | Status |
|:--------|:--------|:-------|
| [adif-mcp](https://github.com/qso-graph/adif-mcp) | ADIF 3.1.7 spec parsing, validation, enumerations (8 tools) | [![PyPI](https://img.shields.io/pypi/v/adif-mcp?label=PyPI&color=blue)](https://pypi.org/project/adif-mcp/) |
| [qso-graph-auth](https://github.com/qso-graph/qso-graph-auth) | Persona management, OS keyring credentials, `qso-auth` CLI | [![PyPI](https://img.shields.io/pypi/v/qso-graph-auth?label=PyPI&color=blue)](https://pypi.org/project/qso-graph-auth/) |

### Logbook Services (Authenticated)

| Package | Service | Tools | Status |
|:--------|:--------|:------|:-------|
| [eqsl-mcp](https://github.com/qso-graph/eqsl-mcp) | [eQSL.cc](https://www.eqsl.cc/) | 6 tools: inbox, verify, AG status, download, last upload, version info | [![PyPI](https://img.shields.io/pypi/v/eqsl-mcp?label=PyPI&color=blue)](https://pypi.org/project/eqsl-mcp/) |
| [lotw-mcp](https://github.com/qso-graph/lotw-mcp) | [LoTW](https://lotw.arrl.org/) | 6 tools: confirmations, QSOs, DXCC credits, download, user activity, version info | [![PyPI](https://img.shields.io/pypi/v/lotw-mcp?label=PyPI&color=blue)](https://pypi.org/project/lotw-mcp/) |
| [qrz-mcp](https://github.com/qso-graph/qrz-mcp) | [QRZ.com](https://www.qrz.com/) | 6 tools: lookup, DXCC, logbook status, download, logbook fetch, version info | [![PyPI](https://img.shields.io/pypi/v/qrz-mcp?label=PyPI&color=blue)](https://pypi.org/project/qrz-mcp/) |
| [hamqth-mcp](https://github.com/qso-graph/hamqth-mcp) | [HamQTH](https://www.hamqth.com/) | 8 tools: lookup, DXCC, bio, activity, DX spots, RBN, verify QSO, version info | [![PyPI](https://img.shields.io/pypi/v/hamqth-mcp?label=PyPI&color=blue)](https://pypi.org/project/hamqth-mcp/) |

### Public Services (No Auth Required)

| Package | Service | Tools | Status |
|:--------|:--------|:------|:-------|
| [pota-mcp](https://github.com/qso-graph/pota-mcp) | [POTA](https://pota.app/) | 8 tools: spots, park info, stats, schedules, location, nearby, activator, version info | [![PyPI](https://img.shields.io/pypi/v/pota-mcp?label=PyPI&color=blue)](https://pypi.org/project/pota-mcp/) |
| [sota-mcp](https://github.com/qso-graph/sota-mcp) | [SOTA](https://www.sota.org.uk/) | 5 tools: spots, alerts, summit info, nearby summits, version info | [![PyPI](https://img.shields.io/pypi/v/sota-mcp?label=PyPI&color=blue)](https://pypi.org/project/sota-mcp/) |
| [iota-mcp](https://github.com/qso-graph/iota-mcp) | [IOTA](https://www.iota-world.org/) | 7 tools: group lookup, island search, DXCC mapping, nearby, stats, version info | [![PyPI](https://img.shields.io/pypi/v/iota-mcp?label=PyPI&color=blue)](https://pypi.org/project/iota-mcp/) |
| [solar-mcp](https://github.com/qso-graph/solar-mcp) | [NOAA SWPC](https://www.swpc.noaa.gov/) | 7 tools: SFI, Kp, solar wind, X-ray flux, band outlook, alerts, version info | [![PyPI](https://img.shields.io/pypi/v/solar-mcp?label=PyPI&color=blue)](https://pypi.org/project/solar-mcp/) |
| [wspr-mcp](https://github.com/qso-graph/wspr-mcp) | [WSPR](https://www.wsprnet.org/) | 9 tools: spots, band activity, top beacons/spotters, propagation, grid, SNR, version info | [![PyPI](https://img.shields.io/pypi/v/wspr-mcp?label=PyPI&color=blue)](https://pypi.org/project/wspr-mcp/) |
| [omiss-mcp](https://github.com/qso-graph/omiss-mcp) | [OMISS](https://www.omiss.net/) | 13 tools: net schedule, nets on the air, member lookup, check-in history, past net check-ins, Statehood, officers, awards, award rules, award recipients, net statistics, set callsign, version info | [![PyPI](https://img.shields.io/pypi/v/omiss-mcp?label=PyPI&color=blue)](https://pypi.org/project/omiss-mcp/) |

### Radio Logging

| Package | Service | Tools | Status |
|:--------|:--------|:------|:-------|
| [n1mm-mcp](https://github.com/qso-graph/n1mm-mcp) | [N1MM Logger+](https://n1mm.hamdocs.com/) | 9 tools: station state, lookup, contacts, bandmap, performance, multipliers, clock, diagnostics, version info | [![PyPI](https://img.shields.io/pypi/v/n1mm-mcp?label=PyPI&color=blue)](https://pypi.org/project/n1mm-mcp/) |
| [netlogger-mcp](https://github.com/qso-graph/netlogger-mcp) | [NetLogger](https://www.netlogger.org/) | 6 tools: active nets, live check-ins and who's up, past nets, past check-ins, set callsign, version info | [![PyPI](https://img.shields.io/pypi/v/netlogger-mcp?label=PyPI&color=blue)](https://pypi.org/project/netlogger-mcp/) |

### Infrastructure

| Package | Purpose | Status |
|:--------|:--------|:-------|
| [qsp-client](https://github.com/qso-graph/qsp-client) | QSP — an MCP client that relays tools to any local LLM (llama.cpp, Ollama, vLLM, SGLang). Formerly qsp-mcp | [![PyPI](https://img.shields.io/pypi/v/qsp-client?label=PyPI&color=blue)](https://pypi.org/project/qsp-client/) |

## Quick Start

```bash
# One-line install (Linux / macOS)
curl -sL https://qso-graph.io/install.sh | bash

# Launch the config manager
qso-graph-config

# Or run a single server directly with uv
uvx solar-mcp
```

Each server works with any MCP client: Claude Desktop, Claude Code, ChatGPT, Cursor, VS Code / GitHub Copilot, Windsurf, Gemini CLI, Goose, and Codex CLI — or use [qsp-client](https://github.com/qso-graph/qsp-client) to relay tools to any local LLM.

## Architecture

```
install.sh (bootstrap)          qso-graph-config (manager)
 └── ~/.qso-graph/               ├── Install / upgrade servers
      ├── venv/                   ├── Credential setup (qso-auth)
      ├── bin/ (PATH)             ├── Dataset downloads (ionis-mcp)
      └── etc/state.json          └── MCP client config generation

qso-graph-auth (identity)       MCP Servers (qso-graph)
 ├── PersonaManager        ──>   eqsl-mcp, qrz-mcp, lotw-mcp, hamqth-mcp
 ├── OS keyring credentials      Each server = 1 uvx       
 └── qso-auth CLI                Each server = 4-8 MCP tools

adif-mcp (ADIF spec)            Public Servers
 └── 8 spec tools          ──>   solar, pota, sota, iota, wspr (no auth)

qsp-client (tool relay)         Local LLM Inference
 └── Stateless pipe        ──>   llama.cpp, Ollama, vLLM, SGLang
     MCP tools → OpenAI           Any model with function calling
     tools format                  Zero cloud dependency
```

### Demos

| Demo | Description | Status |
|:-----|:------------|:-------|
| [qso-graph-demo](https://github.com/qso-graph/qso-graph-demo) | QSO logbook analysis showcase (Next.js / Vercel) | [Live Demo](https://qso-graph-demo.vercel.app/) |
| [dxpedition-demo](https://github.com/qso-graph/dxpedition-demo) | DXpedition propagation analysis — 3Y0K Bouvet Island (Next.js / Vercel) | [Live Demo](https://dxpedition-demo.vercel.app/) |

## Related Projects

| Project | Description |
|:--------|:------------|
| [ionis-mcp](https://github.com/qso-graph/ionis-mcp) | HF propagation analytics from 175M+ signatures (14B observations) — [![PyPI](https://img.shields.io/pypi/v/ionis-mcp?label=PyPI&color=blue)](https://pypi.org/project/ionis-mcp/) |
| [ionis-jupyter](https://github.com/IONIS-AI/ionis-jupyter) | Jupyter notebooks for propagation research |

## Reporting Security Issues

Do NOT open public GitHub issues for security vulnerabilities. Email: ki7mt@yahoo.com with subject `[SECURITY] qso-graph vulnerability report`.

## License

GPL-3.0-or-later
