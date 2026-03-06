# QSO-Graph — MCP Servers for Amateur Radio

[![Live Demo](https://img.shields.io/badge/demo-live-22c55e?style=flat-square&logo=vercel)](https://qso-graph-demo.vercel.app/)
[![Docs](https://img.shields.io/badge/docs-qso--graph.io-3b82f6?style=flat-square)](https://qso-graph.io)

Open-source [Model Context Protocol](https://modelcontextprotocol.io) servers that connect AI assistants to amateur radio services. Ask Claude, ChatGPT, Copilot, or Gemini about your QSOs, confirmations, and logbook data — no manual API wrangling required.

**[View the live demo →](https://qso-graph-demo.vercel.app/)** · **[Documentation →](https://qso-graph.io)**

## Security — Our #1 Priority

**Your credentials never leave the OS keyring.** Every qso-graph server enforces 10 non-negotiable security guarantees:

- Credentials stored in OS keyring only (macOS Keychain, Windows Credential Manager, Linux Secret Service) — never in config files, environment variables, or logs
- Credentials never appear in MCP tool results, error messages, or debug output — enforced by architecture, not policy
- No command injection surface — no `subprocess`, no `shell=True`, no `eval`
- All external connections HTTPS only
- Rate limiting on every API to prevent account bans
- Independent security audit required before every PyPI release

Full details: [Security](https://qso-graph.io/security/)

## Packages

### Foundation

| Package | Purpose | Tools | Status |
|:--------|:--------|:------|:-------|
| [adif-mcp](https://github.com/qso-graph/adif-mcp) | ADIF 3.1.6 spec engine, validation, persona management, keyring credentials | 8 tools: parse, validate, search/list enumerations, distance, heading, version | [PyPI v0.9.3](https://pypi.org/project/adif-mcp/) |

### Logbook Services (Authenticated)

| Package | Service | Tools | Status |
|:--------|:--------|:------|:-------|
| [eqsl-mcp](https://github.com/qso-graph/eqsl-mcp) | [eQSL.cc](https://www.eqsl.cc/) | 4 tools: inbox download, QSO verification, AG status, last upload | [PyPI v0.2.0](https://pypi.org/project/eqsl-mcp/) |
| [lotw-mcp](https://github.com/qso-graph/lotw-mcp) | [LoTW](https://lotw.arrl.org/) | 4 tools: confirmations, QSO query, DXCC credits, user activity | [PyPI v0.2.0](https://pypi.org/project/lotw-mcp/) |
| [qrz-mcp](https://github.com/qso-graph/qrz-mcp) | [QRZ.com](https://www.qrz.com/) | 4 tools: callsign lookup, DXCC resolution, logbook status, logbook fetch | [PyPI v0.2.0](https://pypi.org/project/qrz-mcp/) |
| [hamqth-mcp](https://github.com/qso-graph/hamqth-mcp) | [HamQTH](https://www.hamqth.com/) | 7 tools: lookup, DXCC, bio, activity, DX spots, RBN, verify QSO | [PyPI v0.2.0](https://pypi.org/project/hamqth-mcp/) |

### Public Services (No Auth Required)

| Package | Service | Tools | Status |
|:--------|:--------|:------|:-------|
| [pota-mcp](https://github.com/qso-graph/pota-mcp) | [POTA](https://pota.app/) | 6 tools: live spots, park info, stats, schedules, location search, activator | [PyPI v0.1.1](https://pypi.org/project/pota-mcp/) |
| [sota-mcp](https://github.com/qso-graph/sota-mcp) | [SOTA](https://www.sota.org.uk/) | 5 tools: spots, alerts, summit info, nearby search, activator stats | [PyPI v0.1.1](https://pypi.org/project/sota-mcp/) |
| [iota-mcp](https://github.com/qso-graph/iota-mcp) | [IOTA](https://www.iota-world.org/) | 6 tools: group lookup, island search, DXCC mapping, nearby, stats | [PyPI v0.1.0](https://pypi.org/project/iota-mcp/) |
| [solar-mcp](https://github.com/qso-graph/solar-mcp) | [NOAA SWPC](https://www.swpc.noaa.gov/) | 6 tools: SFI, Kp, solar wind, X-ray flux, band outlook, alerts | [PyPI v0.1.1](https://pypi.org/project/solar-mcp/) |
| [wspr-mcp](https://github.com/qso-graph/wspr-mcp) | [WSPR](https://www.wsprnet.org/) | 5 tools: beacon spots, band activity, propagation paths, TX power | [PyPI v0.1.1](https://pypi.org/project/wspr-mcp/) |

### Desktop

| Package | Purpose | Status |
|:--------|:--------|:-------|
| [qso-graph-manager](https://github.com/qso-graph/qso-graph-manager) | Desktop GUI for managing personas and credentials (Wails/Go/Svelte) | Pre-release |

## Quick Start

```bash
# Install a server
pip install eqsl-mcp

# Set up credentials (via adif-mcp)
pip install adif-mcp
adif-mcp persona create ki7mt --callsign KI7MT
adif-mcp persona provider ki7mt eqsl --username KI7MT
adif-mcp persona secret ki7mt eqsl

# Add to Claude Desktop config and restart
```

Each server works with any MCP client: Claude Desktop, Claude Code, ChatGPT, Cursor, VS Code / GitHub Copilot, and Gemini CLI. See individual package READMEs for configuration.

## Architecture

```
adif-mcp (foundation)          MCP Servers (qso-graph)
 ├── PersonaManager       ──>   eqsl-mcp, qrz-mcp, lotw-mcp, hamqth-mcp
 ├── Keyring credentials        Each server = 1 pip install
 └── ADIF spec tools            Each server = 4-8 MCP tools
```

- **adif-mcp** handles identity and credentials once — all servers share it
- Each server is a standalone `pip install` with a single CLI entry point
- Two public tools per server where possible (no auth needed to try it)
- Python (FastMCP) now, Go single-binary ports planned for production

## Related Projects

| Project | Description |
|:--------|:------------|
| [ionis-mcp](https://github.com/IONIS-AI/ionis-mcp) | HF propagation analytics from 175M+ signatures (14B observations) |
| [ionis-jupyter](https://github.com/IONIS-AI/ionis-jupyter) | Jupyter notebooks for propagation research |

## Reporting Security Issues

Do NOT open public GitHub issues for security vulnerabilities. Email: ki7mt@yahoo.com with subject `[SECURITY] qso-graph vulnerability report`.

## License

GPL-3.0-or-later
