// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'earthquake.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Earthquake _$EarthquakeFromJson(Map<String, dynamic> json) => Earthquake(
      id: (json['id'] as num).toInt(),
      magnitude:
          const StringToDoubleConverter().fromJson(json['magnitude'] as String),
      depth: const StringToDoubleConverter().fromJson(json['depth'] as String),
      latitude:
          const StringToDoubleConverter().fromJson(json['latitude'] as String),
      longitude:
          const StringToDoubleConverter().fromJson(json['longitude'] as String),
      location: json['location'] as String,
      city: json['city'] as String?,
      source: json['source'] as String,
      occurredAt: const StringToDateTimeConverter()
          .fromJson(json['occurred_at'] as String),
      timeAgo: json['time_ago'] as String?,
    );

Map<String, dynamic> _$EarthquakeToJson(Earthquake instance) =>
    <String, dynamic>{
      'id': instance.id,
      'magnitude': const StringToDoubleConverter().toJson(instance.magnitude),
      'depth': const StringToDoubleConverter().toJson(instance.depth),
      'latitude': const StringToDoubleConverter().toJson(instance.latitude),
      'longitude': const StringToDoubleConverter().toJson(instance.longitude),
      'location': instance.location,
      'city': instance.city,
      'source': instance.source,
      'occurred_at':
          const StringToDateTimeConverter().toJson(instance.occurredAt),
      'time_ago': instance.timeAgo,
    };

EarthquakeStats _$EarthquakeStatsFromJson(Map<String, dynamic> json) =>
    EarthquakeStats(
      total: (json['total'] as num).toInt(),
      major: (json['major'] as num).toInt(),
      moderate: (json['moderate'] as num).toInt(),
      minor: (json['minor'] as num).toInt(),
      last24h: (json['last_24h'] as num).toInt(),
      last7d: (json['last_7d'] as num).toInt(),
      strongest: json['strongest'] == null
          ? null
          : Earthquake.fromJson(json['strongest'] as Map<String, dynamic>),
      latest: json['latest'] == null
          ? null
          : Earthquake.fromJson(json['latest'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$EarthquakeStatsToJson(EarthquakeStats instance) =>
    <String, dynamic>{
      'total': instance.total,
      'major': instance.major,
      'moderate': instance.moderate,
      'minor': instance.minor,
      'last_24h': instance.last24h,
      'last_7d': instance.last7d,
      'strongest': instance.strongest,
      'latest': instance.latest,
    };

EarthquakeResponse _$EarthquakeResponseFromJson(Map<String, dynamic> json) =>
    EarthquakeResponse(
      count: (json['count'] as num).toInt(),
      results: (json['results'] as List<dynamic>)
          .map((e) => Earthquake.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$EarthquakeResponseToJson(EarthquakeResponse instance) =>
    <String, dynamic>{
      'count': instance.count,
      'results': instance.results,
    };
