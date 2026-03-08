# QSO-Graph — MCP Servers for Amateur Radio

[![Live Demo](https://img.shields.io/badge/demo-live-22c55e?style=flat-square&logo=vercel)](https://qso-graph-demo.vercel.app/)
[![Docs](https://img.shields.io/badge/docs-qso--graph.io-3b82f6?style=flat-square)](https://qso-graph.io)

Open-source [Model Context Protocol](https://modelcontextprotocol.io) servers that connect AI assistants to amateur radio services. Ask Claude, ChatGPT, Copilot, or Gemini about your QSOs, confirmations, and logbook data — no manual API wrangling required.

**12 packages · 71 tools · one install command.**

**[View the live demo →](https://qso-graph-demo.vercel.app/)** · **[Documentation →](https://qso-graph.io)**

## Install

```bash
curl -sL https://qso-graph.io/install.sh | bash
```

Creates `~/.qso-graph/` with an isolated Python environment, installs the
base MCP servers (6 servers, 38 tools), and adds them to your PATH. Works
on Linux and macOS. No root required.

After install, run `qso-graph-config` to manage servers, credentials,
datasets, and MCP client configuration via an interactive TUI.

**Advanced users** can install directly via pip:

```bash
pip install qso-graph-config                    # Base — 6 servers, 38 tools
pip install "qso-graph-config[auth]"            # + 4 logbook servers (22 tools)
pip install "qso-graph-config[ionis]"           # + ionis-mcp propagation (11 tools)
pip install "qso-graph-config[full]"            # Everything — 12 packages, 71 tools
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
| [qso-graph-config](https://github.com/qso-graph/qso-graph-config) | Installer and manager — TUI, upgrades, config generation, dataset downloads | [PyPI v0.1.0](https://pypi.org/project/qso-graph-config/) |

### Foundation

| Package | Purpose | Status |
|:--------|:--------|:-------|
| [adif-mcp](https://github.com/qso-graph/adif-mcp) | ADIF 3.1.6 spec parsing, validation, enumerations (8 tools) | [PyPI v1.0.0](https://pypi.org/project/adif-mcp/) |
| [qso-graph-auth](https://github.com/qso-graph/qso-graph-auth) | Persona management, OS keyring credentials, `qso-auth` CLI | [PyPI v0.1.0](https://pypi.org/project/qso-graph-auth/) |

### Logbook Services (Authenticated)

| Package | Service | Tools | Status |
|:--------|:--------|:------|:-------|
| [eqsl-mcp](https://github.com/qso-graph/eqsl-mcp) | [eQSL.cc](https://www.eqsl.cc/) | 5 tools: inbox, verify, AG status, download, last upload | [PyPI v0.3.0](https://pypi.org/project/eqsl-mcp/) |
| [lotw-mcp](https://github.com/qso-graph/lotw-mcp) | [LoTW](https://lotw.arrl.org/) | 5 tools: confirmations, QSOs, DXCC credits, download, user activity | [PyPI v0.3.0](https://pypi.org/project/lotw-mcp/) |
| [qrz-mcp](https://github.com/qso-graph/qrz-mcp) | [QRZ.com](https://www.qrz.com/) | 5 tools: lookup, DXCC, logbook status, download, logbook fetch | [PyPI v0.3.0](https://pypi.org/project/qrz-mcp/) |
| [hamqth-mcp](https://github.com/qso-graph/hamqth-mcp) | [HamQTH](https://www.hamqth.com/) | 7 tools: lookup, DXCC, bio, activity, DX spots, RBN, verify QSO | [PyPI v0.3.0](https://pypi.org/project/hamqth-mcp/) |

### Public Services (No Auth Required)

| Package | Service | Tools | Status |
|:--------|:--------|:------|:-------|
| [pota-mcp](https://github.com/qso-graph/pota-mcp) | [POTA](https://pota.app/) | 6 tools: spots, park info, stats, schedules, location, activator | [PyPI v0.1.1](https://pypi.org/project/pota-mcp/) |
| [sota-mcp](https://github.com/qso-graph/sota-mcp) | [SOTA](https://www.sota.org.uk/) | 4 tools: spots, alerts, summit info, nearby summits | [PyPI v0.1.4](https://pypi.org/project/sota-mcp/) |
| [iota-mcp](https://github.com/qso-graph/iota-mcp) | [IOTA](https://www.iota-world.org/) | 6 tools: group lookup, island search, DXCC mapping, nearby, stats | [PyPI v0.1.0](https://pypi.org/project/iota-mcp/) |
| [solar-mcp](https://github.com/qso-graph/solar-mcp) | [NOAA SWPC](https://www.swpc.noaa.gov/) | 6 tools: SFI, Kp, solar wind, X-ray flux, band outlook, alerts | [PyPI v0.2.0](https://pypi.org/project/solar-mcp/) |
| [wspr-mcp](https://github.com/qso-graph/wspr-mcp) | [WSPR](https://www.wsprnet.org/) | 8 tools: spots, band activity, top beacons/spotters, propagation, grid, SNR | [PyPI v0.2.0](https://pypi.org/project/wspr-mcp/) |

### Desktop

| Package | Purpose | Status |
|:--------|:--------|:-------|
| [qso-graph-manager](https://github.com/qso-graph/qso-graph-manager) | Desktop GUI for managing personas and credentials (Wails/Go/Svelte) | Pre-release |

## Quick Start

```bash
# One-line install (Linux / macOS)
curl -sL https://qso-graph.io/install.sh | bash

# Launch the config manager
qso-graph-config

# Or install a single server directly
pip install solar-mcp
```

Each server works with any MCP client: Claude Desktop, Claude Code, ChatGPT, Cursor, VS Code / GitHub Copilot, Windsurf, Gemini CLI, Goose, and Codex CLI.

## Architecture

```
install.sh (bootstrap)          qso-graph-config (manager)
 └── ~/.qso-graph/               ├── Install / upgrade servers
      ├── venv/                   ├── Credential setup (qso-auth)
      ├── bin/ (PATH)             ├── Dataset downloads (ionis-mcp)
      └── etc/state.json          └── MCP client config generation

qso-graph-auth (identity)       MCP Servers (qso-graph)
 ├── PersonaManager        ──>   eqsl-mcp, qrz-mcp, lotw-mcp, hamqth-mcp
 ├── OS keyring credentials      Each server = 1 pip install
 └── qso-auth CLI                Each server = 4-8 MCP tools

adif-mcp (ADIF spec)            Public Servers
 └── 8 spec tools          ──>   solar, pota, sota, iota, wspr (no auth)
```

## Related Projects

| Project | Description |
|:--------|:------------|
| [ionis-mcp](https://github.com/IONIS-AI/ionis-mcp) | HF propagation analytics from 175M+ signatures (14B observations) |
| [ionis-jupyter](https://github.com/IONIS-AI/ionis-jupyter) | Jupyter notebooks for propagation research |

## Reporting Security Issues

Do NOT open public GitHub issues for security vulnerabilities. Email: ki7mt@yahoo.com with subject `[SECURITY] qso-graph vulnerability report`.

## License

GPL-3.0-or-later
