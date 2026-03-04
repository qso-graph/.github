# QSO-Graph — MCP Servers for Amateur Radio

Open-source [Model Context Protocol](https://modelcontextprotocol.io) servers that connect AI assistants to amateur radio services. Ask Claude, ChatGPT, Copilot, or Gemini about your QSOs, confirmations, and logbook data — no manual API wrangling required.

Built on [adif-mcp](https://github.com/KI7MT/adif-mcp) for identity, credential management, and ADIF specification tools.

## Security — Our #1 Priority

**Your credentials never leave the OS keyring.** Every qso-graph server enforces 10 non-negotiable security guarantees:

- Credentials stored in OS keyring only (macOS Keychain, Windows Credential Manager, Linux Secret Service) — never in config files, environment variables, or logs
- Credentials never appear in MCP tool results, error messages, or debug output — enforced by architecture, not policy
- No command injection surface — no `subprocess`, no `shell=True`, no `eval`
- All external connections HTTPS only
- Rate limiting on every API to prevent account bans
- Independent security audit required before every PyPI release

Full framework: [MCP-SECURITY-FRAMEWORK.md](https://github.com/IONIS-AI/ionis-devel/blob/main/planning/MCP-SECURITY-FRAMEWORK.md)

## Packages

| Package | Service | Tools | Status |
|:--------|:--------|:------|:-------|
| [eqsl-mcp](https://github.com/qso-graph/eqsl-mcp) | [eQSL.cc](https://www.eqsl.cc/) | Inbox download, QSO verification, AG status, last upload | [PyPI](https://pypi.org/project/eqsl-mcp/) |
| [qrz-mcp](https://github.com/qso-graph/qrz-mcp) | [QRZ.com](https://www.qrz.com/) | Callsign lookup, DXCC resolution, logbook queries | [PyPI](https://pypi.org/project/qrz-mcp/) |
| [clublog-mcp](https://github.com/qso-graph/clublog-mcp) | [Club Log](https://clublog.org/) | DXCC resolution, log search, propagation activity, Most Wanted, expeditions | v0.1.0 |
| [lotw-mcp](https://github.com/qso-graph/lotw-mcp) | [LoTW](https://lotw.arrl.org/) | Confirmations, QSO query, DXCC credits, user activity | v0.1.0 |
| [hamqth-mcp](https://github.com/qso-graph/hamqth-mcp) | [HamQTH](https://www.hamqth.com/) | Callsign lookup (free QRZ alternative) | Planned |
| [pota-mcp](https://github.com/qso-graph/pota-mcp) | [POTA](https://pota.app/) | Park lookup, activator/hunter stats, spots | Planned |
| [sota-mcp](https://github.com/qso-graph/sota-mcp) | [SOTA](https://www.sota.org.uk/) | Summit lookup, activator stats, spots | Planned |
| [solar-mcp](https://github.com/qso-graph/solar-mcp) | [NOAA SWPC](https://www.swpc.noaa.gov/) | Solar indices, space weather, DSCOVR, alerts | Planned |
| [wspr-mcp](https://github.com/qso-graph/wspr-mcp) | [WSPR](https://www.wsprnet.org/) | Band openings, path analysis, solar correlation | Planned |

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
 ├── PersonaManager       ──>   eqsl-mcp, qrz-mcp, clublog-mcp, ...
 ├── Keyring credentials        Each server = 1 pip install
 └── ADIF spec tools            Each server = 3-10 MCP tools
```

- **adif-mcp** handles identity and credentials once — all servers share it
- Each server is a standalone `pip install` with a single CLI entry point
- Two public tools per server where possible (no auth needed to try it)
- Python (FastMCP) now, Go single-binary ports planned for production

## Related Projects

| Project | Description |
|:--------|:------------|
| [adif-mcp](https://github.com/KI7MT/adif-mcp) | Foundation — ADIF spec tools, persona management, keyring credentials |
| [ionis-mcp](https://github.com/IONIS-AI/ionis-mcp) | HF propagation analytics from 175M+ signatures (14B observations) |
| [ionis-jupyter](https://github.com/IONIS-AI/ionis-jupyter) | Jupyter notebooks for propagation research |

## Reporting Security Issues

Do NOT open public GitHub issues for security vulnerabilities. Email: ki7mt@yahoo.com with subject `[SECURITY] qso-graph vulnerability report`.

## License

GPL-3.0-or-later
