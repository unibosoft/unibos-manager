/// module model representing a UNIBOS module
class UnibosModule {
  final String id;
  final String name;
  final String description;
  final String icon;
  final String route;
  final bool isEnabled;
  final ModuleCategory category;

  const UnibosModule({
    required this.id,
    required this.name,
    required this.description,
    required this.icon,
    required this.route,
    this.isEnabled = true,
    this.category = ModuleCategory.app,
  });
}

enum ModuleCategory {
  app,     // user-facing apps
  tool,    // utility tools
  system,  // system modules
}

/// all available modules
class UnibosModules {
  UnibosModules._();

  static const List<UnibosModule> all = [
    // main modules
    UnibosModule(
      id: 'currencies',
      name: 'currencies',
      description: 'exchange rates and crypto prices',
      icon: '💰',
      route: '/modules/currencies',
    ),
    UnibosModule(
      id: 'birlikteyiz',
      name: 'birlikteyiz',
      description: 'community locations and events',
      icon: '🗺️',
      route: '/modules/birlikteyiz',
    ),
    UnibosModule(
      id: 'movies',
      name: 'movies',
      description: 'movie collection and watchlist',
      icon: '🎬',
      route: '/modules/movies',
    ),
    UnibosModule(
      id: 'music',
      name: 'music',
      description: 'music library and playlists',
      icon: '🎵',
      route: '/modules/music',
    ),
    UnibosModule(
      id: 'documents',
      name: 'documents',
      description: 'document management and ocr',
      icon: '📄',
      route: '/modules/documents',
    ),
    UnibosModule(
      id: 'personal-inflation',
      name: 'personal inflation',
      description: 'track your personal expenses',
      icon: '📈',
      route: '/modules/personal-inflation',
    ),
    UnibosModule(
      id: 'cctv',
      name: 'cctv',
      description: 'camera monitoring system',
      icon: '📸',
      route: '/modules/cctv',
    ),
    UnibosModule(
      id: 'restopos',
      name: 'restopos',
      description: 'restaurant point of sale',
      icon: '🍽️',
      route: '/modules/restopos',
    ),
    UnibosModule(
      id: 'wimm',
      name: 'wimm',
      description: 'where is my money',
      icon: '💸',
      route: '/modules/wimm',
    ),
    UnibosModule(
      id: 'wims',
      name: 'wims',
      description: 'where is my stuff',
      icon: '📦',
      route: '/modules/wims',
    ),
    UnibosModule(
      id: 'solitaire',
      name: 'solitaire',
      description: 'classic card game',
      icon: '🃏',
      route: '/modules/solitaire',
    ),
    UnibosModule(
      id: 'store',
      name: 'store',
      description: 'app and module store',
      icon: '🏪',
      route: '/modules/store',
    ),
    UnibosModule(
      id: 'recaria',
      name: 'recaria',
      description: 'receipt management',
      icon: '🧾',
      route: '/modules/recaria',
    ),
  ];

  static UnibosModule? getById(String id) {
    try {
      return all.firstWhere((m) => m.id == id);
    } catch (e) {
      return null;
    }
  }
}
