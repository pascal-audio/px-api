# Changelog

For detailed API status and roadmap, see docs/README.md

## v1.0.0 (November 2025)

Release of PX JSON-RPC API (JAPI) for third-party integration.

### API Status

## API Status & Roadmap

### ✅ Stable (v1.0.0 - Production Ready)

- **Setup API** - All paths finalized, backward compatible in v1.x
- **Device API** - All methods stable
- **Preset API** - Locking mechanism finalized
- **Metrics API** - Real-time metrics stable

### ⚠️ Work in Progress

- **Status API** - Structure may change in v1.x
  - Use with caution in production
  - Existing fields may change
  - New fields may be added
  - **Recommendation:** Use setup subscriptions for critical workflows

### 🔮 Future (Roadmap)

**v1.1.0** 
- Status API stabilization

**v1.2.0** 
- Authentication


See **[05-best-practices.md](05-best-practices.md)** revision history section for detailed changelog.

---

### Package Contents

**Documentation:**
- 6 comprehensive markdown files
- Complete API reference with examples
- Configuration path reference
- Best practices guide

**Tooling:**
- Virtual device emulators (3 platforms)
- Python CLI tool (japi_cli)
- TypeScript/Python client libraries
- 224 JSON schemas for validation

**Audio Features:**
- 3-layer processing (User → Array → Preset)
- 10-band parametric EQ per channel
- FIR filters, crossovers, limiters
- Channel preset save/recall
- Real-time metrics and notifications
