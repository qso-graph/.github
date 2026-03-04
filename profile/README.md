# QSO-Graph — MCP Servers for Amateur Radio

Open-source [Model Context Protocol](https://modelcontextprotocol.io) servers that connect AI assistants to amateur radio services. Ask Claude, ChatGPT, Copilot, or Gemini about your QSOs, confirmations, and logbook data — no manual API wrangling required.

Built on [adif-mcp](https://github.com/KI7MT/adif-mcp) for identity, credential management, and ADIF specification tools.

## Packages

| Package | Service | Tools | Status |
|:--------|:--------|:------|:-------|
| [eqsl-mcp](https://github.com/qso-graph/eqsl-mcp) | [eQSL.cc](https://www.eqsl.cc/) | Inbox download, QSO verification, AG status, last upload | [PyPI](https://pypi.org/project/eqsl-mcp/) |
| [qrz-mcp](https://github.com/qso-graph/qrz-mcp) | [QRZ.com](https://www.qrz.com/) | Callsign lookup, DXCC resolution, logbook queries | [PyPI](https://pypi.org/project/qrz-mcp/) |
| [clublog-mcp](https://github.com/qso-graph/clublog-mcp) | [Club Log](https://clublog.org/) | Log search, DXCC status, most-wanted, OQRS | Planned |
| [lotw-mcp](https://github.com/qso-graph/lotw-mcp) | [LoTW](https://lotw.arrl.org/) | QSO query, QSL status, DXCC credit | Planned |
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

## License

GPL-3.0-or-later
