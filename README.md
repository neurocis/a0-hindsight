# 🧠 Hindsight Memory Plugin for Agent Zero

Augments Agent Zero's built-in memory with [Hindsight](https://github.com/vectorize-io/hindsight) by [Vectorize.io](https://vectorize.io). Gives Agent Zero persistent, semantically-rich memory that goes beyond simple vector similarity — with disposition-aware context generation.

## What It Does

| Feature | Description |
|---------|-------------|
| **Automatic Retain** | Conversation memories are extracted and stored in Hindsight banks after each interaction |
| **Enhanced Recall** | Memory recall is enriched with Hindsight's semantic search alongside the built-in vector memory |
| **Reflect Context** | Disposition-aware context is generated and injected into the system prompt |
| **Project Isolation** | Memory banks are automatically scoped by project for clean separation |
| **Graceful Degradation** | If Hindsight is unavailable, the agent continues normally with built-in memory |
| **Settings UI** | Configure all settings directly in A0's settings panel |
| **Plugin System Conformant** | Built for A0's plugin architecture (plugin.yaml, extensions, settings) |

## How It Works

```
┌─────────────┐     retain        ┌──────────────┐     reflect       ┌──────────────┐
│  Agent Zero  │ ───────────────▶  │  Hindsight   │ ───────────────▶  │  Disposition  │
│  (your chat) │                   │  (memory)    │   context gen     │  (insights)   │
└──────┬───────┘                   └──────┬───────┘                   └──────────────┘
       │                                  │
       │◀──── recall + reflect ───────────┘
       │      (system prompt injection)
```

1. **Retain** — After each conversation turn, key facts and information are extracted and stored in Hindsight via the `monologue_end` extension
2. **Recall** — On each recall cycle, Hindsight is queried alongside the built-in memory for enriched semantic search results
3. **Reflect** — Hindsight generates disposition-aware context that is injected into the system prompt

## Installation

### 1. Clone into Agent Zero's user plugins directory

```bash
cd /a0/usr/plugins
git clone https://github.com/YOUR_USERNAME/a0-plugin-hindsight.git hindsight
```

Or copy the plugin files directly into `/a0/usr/plugins/hindsight/`.

### 2. Install dependencies

```bash
pip install hindsight-client>=0.4.0
```

### 3. Set up a Hindsight server

Follow the [Hindsight installation guide](https://github.com/vectorize-io/hindsight) to run a local server:

```bash
docker run -p 8888:8888 vectorize/hindsight
```

Or use the Vectorize.io hosted service.

### 4. Configure in Agent Zero

1. Go to **Settings → Secrets** and add:
   - `HINDSIGHT_BASE_URL` — your Hindsight server URL (e.g. `http://localhost:8888`)
   - `HINDSIGHT_API_KEY` — (optional) API key if required by your server

2. Go to **Settings → Plugins** and enable **Hindsight Memory**

3. (Optional) Click **Configure** on the plugin to adjust:
   - Bank ID prefix
   - Enable/disable retain, recall, reflect individually
   - Recall/reflect budgets and token limits
   - Cache TTL

### 5. Restart Agent Zero

The plugin will be discovered on restart. You'll see `[Hindsight] Integration enabled for bank: a0-default` in the logs.

## Plugin Structure

```
hindsight/
├── plugin.yaml                          # Plugin manifest
├── default_config.yaml                  # Settings defaults
├── requirements.txt                     # hindsight-client>=0.4.0
├── hooks.py                             # Install/update hooks
├── execute.py                           # User-triggered setup & health check
├── helpers/
│   ├── __init__.py
│   └── hindsight_helper.py              # Core integration logic
├── extensions/
│   └── python/
│       ├── monologue_start/
│       │   └── _20_hindsight_init.py    # Initialize Hindsight on agent start
│       ├── monologue_end/
│       │   └── _52_hindsight_retain.py  # Retain memories to Hindsight
│       ├── message_loop_prompts_after/
│       │   └── _51_hindsight_recall.py  # Enrich recall with Hindsight
│       └── system_prompt/
│           └── _30_hindsight_reflect.py # Inject reflect context into prompt
├── prompts/
│   ├── hindsight.retain_extract.sys.md  # Memory extraction prompt
│   ├── hindsight.recall.md              # Recall injection template
│   └── hindsight.reflect.md             # Reflect injection template
├── webui/
│   └── config.html                      # Settings UI
└── README.md
```

## Configuration

### Secrets (Settings → Secrets)

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `HINDSIGHT_BASE_URL` | ✅ Yes | — | Hindsight server URL (e.g. `http://localhost:8888`) |
| `HINDSIGHT_API_KEY` | No | — | API key (optional for local servers) |

### Plugin Settings (Settings → Plugins → Hindsight → Configure)

| Setting | Default | Description |
|---------|---------|-------------|
| Bank ID Prefix | `a0` | Prefix for memory bank IDs |
| Enable Retain | `true` | Store memories to Hindsight |
| Enable Recall | `true` | Enrich recall with Hindsight search |
| Enable Reflect | `true` | Inject reflect context into prompt |
| Recall Max Tokens | `4096` | Max tokens for recall results |
| Recall Budget | `mid` | Compute budget for recall |
| Reflect Budget | `low` | Compute budget for reflect |
| Reflect Max Tokens | `500` | Max tokens for reflect context |
| Cache TTL | `120` seconds | How long to cache reflect context |
| Debug Logging | `false` | Verbose logging |

## Hindsight Concepts

| Concept | Description |
|---------|-------------|
| **Bank** | A memory container scoped by project context |
| **Retain** | Store information as memories in a bank |
| **Recall** | Semantic search across stored memories |
| **Reflect** | Generate disposition-aware responses using stored knowledge |
| **Disposition** | Personality traits (skepticism, literalism, empathy) that affect how reflect generates context |

## Requirements

- Agent Zero (with plugin system)
- Python 3.12+
- `hindsight-client` >= 0.4.0
- A running Hindsight server (local Docker or hosted)

## Links

- [Hindsight GitHub](https://github.com/vectorize-io/hindsight)
- [Vectorize.io](https://vectorize.io)
- [Agent Zero](https://github.com/agent0ai/agent-zero)

## License

MIT
