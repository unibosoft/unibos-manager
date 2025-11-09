import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:permission_handler/permission_handler.dart';
import 'dart:async';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/earthquake.dart';
import 'api_service.dart';

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin _notifications =
      FlutterLocalNotificationsPlugin();

  bool _initialized = false;
  Timer? _pollingTimer;
  String? _lastEarthquakeId;

  // initialize notification service
  Future<void> initialize() async {
    if (_initialized) return;

    // android initialization
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');

    // ios initialization
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _notifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );

    // request permission
    await _requestPermission();

    // create notification channel for android
    await _createNotificationChannel();

    // load last earthquake id
    await _loadLastEarthquakeId();

    _initialized = true;
  }

  // request notification permission
  Future<bool> _requestPermission() async {
    final status = await Permission.notification.request();
    return status.isGranted;
  }

  // create android notification channel
  Future<void> _createNotificationChannel() async {
    const channel = AndroidNotificationChannel(
      'earthquake_alerts',
      'deprem uyarıları',
      description: 'deprem olduğunda bildirim gönderir',
      importance: Importance.high,
      sound: RawResourceAndroidNotificationSound('notification'),
    );

    await _notifications
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>()
        ?.createNotificationChannel(channel);
  }

  // notification tapped callback
  void _onNotificationTapped(NotificationResponse response) {
    // handle notification tap
    // you can navigate to earthquake detail screen here
  }

  // show earthquake notification
  Future<void> showEarthquakeNotification(Earthquake earthquake) async {
    if (!_initialized) await initialize();

    // determine notification priority based on magnitude
    String title;
    String emoji;
    Priority priority;
    Importance importance;
    String channelId = 'earthquake_alerts';

    if (earthquake.magnitude >= 5.0) {
      title = '🚨 büyük deprem!';
      emoji = '🚨';
      priority = Priority.high;
      importance = Importance.max;
    } else if (earthquake.magnitude >= 4.0) {
      title = '⚠️ orta şiddetli deprem';
      emoji = '⚠️';
      priority = Priority.high;
      importance = Importance.high;
    } else if (earthquake.magnitude >= 3.0) {
      title = '📊 deprem';
      emoji = '📊';
      priority = Priority.defaultPriority;
      importance = Importance.defaultImportance;
    } else {
      title = 'ℹ️ küçük deprem';
      emoji = 'ℹ️';
      priority = Priority.low;
      importance = Importance.low;
    }

    final body =
        '${earthquake.magnitude} büyüklük - ${earthquake.location}\nderinlik: ${earthquake.depth} km';

    final androidDetails = AndroidNotificationDetails(
      channelId,
      'deprem uyarıları',
      channelDescription: 'deprem olduğunda bildirim gönderir',
      importance: importance,
      priority: priority,
      ticker: 'deprem',
      styleInformation: BigTextStyleInformation(body),
      icon: '@mipmap/ic_launcher',
    );

    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    final details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _notifications.show(
      earthquake.id.hashCode,
      '$emoji ${earthquake.magnitude} - $title',
      body,
      details,
      payload: earthquake.id.toString(),
    );
  }

  // start polling for new earthquakes
  void startPolling({Duration interval = const Duration(minutes: 5)}) {
    if (_pollingTimer != null) return;

    _pollingTimer = Timer.periodic(interval, (_) async {
      await _checkForNewEarthquakes();
    });
  }

  // stop polling
  void stopPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = null;
  }

  // check for new earthquakes
  Future<void> _checkForNewEarthquakes() async {
    try {
      final apiService = ApiClient.createApiService();
      final response = await apiService.getRecentEarthquakes(1);

      print('🔔 Polling: Checking for new earthquakes...');

      if (response.count > 0 && response.results.isNotEmpty) {
        final latestEarthquake = response.results.first;
        final latestId = latestEarthquake.id.toString();

        print('🔔 Latest earthquake: ID=$latestId, M=${latestEarthquake.magnitude}, Location=${latestEarthquake.location}');
        print('🔔 Last known ID: $_lastEarthquakeId');

        // check if this is a new earthquake
        if (_lastEarthquakeId != latestId) {
          print('🔔 NEW earthquake detected!');

          // only notify for significant earthquakes (magnitude >= 3.0)
          if (latestEarthquake.magnitude >= 3.0) {
            print('🔔 Showing notification for M${latestEarthquake.magnitude}');
            await showEarthquakeNotification(latestEarthquake);
          } else {
            print('🔔 Magnitude too low (${latestEarthquake.magnitude}), skipping notification');
          }

          // save last earthquake id
          _lastEarthquakeId = latestId;
          await _saveLastEarthquakeId();
        } else {
          print('🔔 No new earthquake (same ID)');
        }
      }
    } catch (e) {
      print('🔔 Error checking earthquakes: $e');
    }
  }

  // load last earthquake id from storage
  Future<void> _loadLastEarthquakeId() async {
    final prefs = await SharedPreferences.getInstance();
    _lastEarthquakeId = prefs.getString('last_earthquake_id');
  }

  // save last earthquake id to storage
  Future<void> _saveLastEarthquakeId() async {
    if (_lastEarthquakeId != null) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('last_earthquake_id', _lastEarthquakeId!);
    }
  }

  // cancel all notifications
  Future<void> cancelAll() async {
    await _notifications.cancelAll();
  }

  // cancel specific notification
  Future<void> cancel(int id) async {
    await _notifications.cancel(id);
  }
}
