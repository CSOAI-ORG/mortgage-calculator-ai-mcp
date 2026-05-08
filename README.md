<div align="center">

# Mortgage Calculator Ai MCP

**MCP server for mortgage calculator ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-mortgage-calculator-ai-mcp)](https://pypi.org/project/meok-mortgage-calculator-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Mortgage Calculator Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `calculate_mortgage` | Calculate monthly mortgage payment with optional down payment. Rate is annual pe |
| `compare_rates` | Compare monthly payments across multiple interest rates side by side. |
| `amortization_schedule` | Generate a yearly amortization schedule showing principal vs interest breakdown. |
| `affordability_check` | Estimate maximum affordable home price based on income and debts using 28/36 rul |

## Installation

```bash
pip install meok-mortgage-calculator-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mortgage-calculator-ai": {
      "command": "python",
      "args": ["-m", "meok_mortgage_calculator_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
