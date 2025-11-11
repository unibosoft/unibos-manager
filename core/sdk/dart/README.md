# UNIBOS Dart/Flutter SDK

Flutter SDK for developing UNIBOS mobile module applications.

## Overview

The UNIBOS Flutter SDK provides a standardized way to create mobile apps for UNIBOS modules.

## Planned Components

### 1. API Client
- REST API integration
- WebSocket support
- Authentication handling
- Error handling

### 2. State Management
- Module state management
- Global state integration
- Reactive updates

### 3. UI Components
- Common widgets
- Theme system
- Navigation helpers
- Form utilities

### 4. Platform Integration
- Camera access
- File storage
- Geolocation
- Push notifications

## Installation

```yaml
dependencies:
  unibos_flutter: ^1.0.0
```

## Quick Start

```dart
import 'package:unibos_flutter/unibos_flutter.dart';

class MyModuleApp extends UnibosModuleApp {
  @override
  String get moduleId => 'my_module';

  @override
  Widget build(BuildContext context) {
    return ModuleScaffold(
      title: 'My Module',
      child: MyModuleHome(),
    );
  }
}
```

## Documentation

Full documentation will be available at: `/docs/sdk/dart/`

## Status

🔵 **In Development** - Part of Phase 8: Everything App Platform Architecture

## License

Copyright © 2025 Berk Hatırlı
