import 'package:json_annotation/json_annotation.dart';

part 'earthquake.g.dart';

// Custom converter for string to double
class StringToDoubleConverter implements JsonConverter<double, String> {
  const StringToDoubleConverter();

  @override
  double fromJson(String json) => double.parse(json);

  @override
  String toJson(double object) => object.toString();
}

// Custom converter for string to DateTime
class StringToDateTimeConverter implements JsonConverter<DateTime, String> {
  const StringToDateTimeConverter();

  @override
  DateTime fromJson(String json) => DateTime.parse(json.replaceAll(' ', 'T'));

  @override
  String toJson(DateTime object) => object.toIso8601String();
}

@JsonSerializable()
class Earthquake {
  final int id;

  @StringToDoubleConverter()
  final double magnitude;

  @StringToDoubleConverter()
  final double depth;

  @StringToDoubleConverter()
  final double latitude;

  @StringToDoubleConverter()
  final double longitude;
  final String location;
  final String? city;
  final String source;

  @JsonKey(name: 'occurred_at')
  @StringToDateTimeConverter()
  final DateTime occurredAt;

  @JsonKey(name: 'time_ago')
  final String? timeAgo;

  Earthquake({
    required this.id,
    required this.magnitude,
    required this.depth,
    required this.latitude,
    required this.longitude,
    required this.location,
    this.city,
    required this.source,
    required this.occurredAt,
    this.timeAgo,
  });

  factory Earthquake.fromJson(Map<String, dynamic> json) =>
      _$EarthquakeFromJson(json);

  Map<String, dynamic> toJson() => _$EarthquakeToJson(this);

  // Magnitude color
  String get magnitudeColor {
    if (magnitude >= 5.0) return '#ff4444';
    if (magnitude >= 4.0) return '#ff8c00';
    if (magnitude >= 3.0) return '#ffff00';
    return '#00ff00';
  }

  // Magnitude size for map markers
  double get markerSize {
    if (magnitude >= 5.0) return 20.0;
    if (magnitude >= 4.0) return 16.0;
    if (magnitude >= 3.0) return 12.0;
    return 8.0;
  }
}

@JsonSerializable()
class EarthquakeStats {
  final int total;
  final int major;
  final int moderate;
  final int minor;

  @JsonKey(name: 'last_24h')
  final int last24h;

  @JsonKey(name: 'last_7d')
  final int last7d;

  final Earthquake? strongest;
  final Earthquake? latest;

  EarthquakeStats({
    required this.total,
    required this.major,
    required this.moderate,
    required this.minor,
    required this.last24h,
    required this.last7d,
    this.strongest,
    this.latest,
  });

  factory EarthquakeStats.fromJson(Map<String, dynamic> json) =>
      _$EarthquakeStatsFromJson(json);

  Map<String, dynamic> toJson() => _$EarthquakeStatsToJson(this);
}

@JsonSerializable()
class EarthquakeResponse {
  final int count;
  final List<Earthquake> results;

  EarthquakeResponse({
    required this.count,
    required this.results,
  });

  factory EarthquakeResponse.fromJson(Map<String, dynamic> json) =>
      _$EarthquakeResponseFromJson(json);

  Map<String, dynamic> toJson() => _$EarthquakeResponseToJson(this);
}
