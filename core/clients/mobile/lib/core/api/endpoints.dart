/// api endpoint constants
class Endpoints {
  Endpoints._();

  // auth endpoints
  static const String login = '/auth/login/';
  static const String register = '/auth/register/';
  static const String tokenRefresh = '/auth/token/refresh/';
  static const String logout = '/auth/logout/';
  static const String offlineLogin = '/auth/login/offline/';

  // user endpoints
  static const String userMe = '/users/me/';
  static const String userProfile = '/users/profile/';

  // health endpoints (relative to base url, not api)
  static const String healthQuick = '/health/quick/';
  static const String healthFull = '/health/full/';

  // sync endpoints
  static const String syncInit = '/sync/init/';
  static const String syncPull = '/sync/pull/';
  static const String syncPush = '/sync/push/';
  static const String syncComplete = '/sync/complete/';
  static const String syncStatus = '/sync/status/';
  static const String syncConflicts = '/sync/conflicts/';
  static const String syncOffline = '/sync/offline/';

  // export control endpoints
  static const String exportSettings = '/sync/export/settings/';
  static const String exportKillSwitch = '/sync/export/kill-switch/';
  static const String exportCheck = '/sync/export/check/';
  static const String exportLogs = '/sync/export/logs/';

  // node endpoints
  static const String nodesRegister = '/nodes/register/';
  static const String nodesDiscover = '/nodes/discover/';

  // p2p endpoints
  static const String p2pStatus = '/p2p/status/';
  static const String p2pStart = '/p2p/start/';
  static const String p2pStop = '/p2p/stop/';
  static const String p2pPeers = '/p2p/peers/';

  // module endpoints
  static const String currencies = '/currencies/';
  static const String movies = '/movies/';
  static const String music = '/music/';
  static const String birlikteyiz = '/birlikteyiz/';
  static const String documents = '/documents/';
  static const String cctv = '/cctv/';
  static const String restopos = '/restopos/';
  static const String wimm = '/wimm/';
  static const String wims = '/wims/';
  static const String personalInflation = '/personal-inflation/';
  static const String solitaire = '/solitaire/';
  static const String store = '/store/';
  static const String recaria = '/recaria/';
}
