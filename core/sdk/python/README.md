# UNIBOS Python SDK

Python SDK for developing UNIBOS modules with multi-platform support.

## Overview

The UNIBOS SDK provides a standardized way to create modules that can run across different platforms (web, CLI, mobile).

## Planned Components

### 1. Base Module Class
- Abstract base class for all modules
- Platform detection
- Configuration management
- Lifecycle hooks

### 2. Platform Helpers
- **Web**: Django view helpers, template utilities
- **CLI**: Command framework, output formatters
- **API**: REST API utilities, serialization helpers

### 3. Core Services
- Authentication integration
- Storage integration
- Cache integration
- Event bus integration

### 4. Utilities
- Logging
- Error handling
- Validation
- Testing utilities

## Installation

```bash
pip install unibos-sdk
```

## Quick Start

```python
from unibos_sdk import UnibosModule

class MyModule(UnibosModule):
    def __init__(self):
        super().__init__(
            id="my_module",
            version="1.0.0"
        )

    def initialize(self):
        # Module initialization
        pass
```

## Documentation

Full documentation will be available at: `/docs/sdk/python/`

## Status

🔵 **In Development** - Part of Phase 8: Everything App Platform Architecture

## License

Copyright © 2025 Berk Hatırlı
