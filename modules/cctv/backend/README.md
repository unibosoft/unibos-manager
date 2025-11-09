# CCTV Module - UNIBOS Security Camera Management

Professional security camera management system with TP-Link Tapo camera support and Kerberos.io integration.

## Features

### Core Functionality
- **Live Streaming**: Real-time camera feeds with multiple quality options
- **Recording Management**: Continuous, scheduled, and motion-triggered recording
- **Multi-Camera Grid**: Monitor multiple cameras simultaneously (2x2, 3x3, 4x4 layouts)
- **PTZ Control**: Pan-Tilt-Zoom control for supported cameras
- **Alert System**: Motion detection, person detection, and custom alerts
- **Storage Management**: Automatic retention policies and storage optimization

### Camera Support
- TP-Link Tapo Series (C200, C210, C310, C320WS)
- Generic RTSP cameras
- ONVIF compatible devices
- Kerberos.io integration for advanced processing

## Technical Stack

### Backend Components
- **Django Models**: Comprehensive database schema for cameras, recordings, alerts
- **RTSP Streaming**: Direct RTSP stream handling with authentication
- **FFmpeg Integration**: Video transcoding and recording
- **WebRTC Support**: Low-latency browser streaming (planned)
- **OpenCV**: Motion detection and video analytics (planned)

### Frontend Components
- **Live View**: MJPEG streaming proxy for browser compatibility
- **Grid Layout**: Flexible multi-camera monitoring
- **Recording Playback**: HTML5 video player with timeline
- **Responsive Design**: Dark theme with orange (#ff8c00) accent

## Installation

### Prerequisites
```bash
# Required packages
pip install opencv-python-headless
pip install numpy
pip install pillow

# Optional for advanced features
apt-get install ffmpeg  # For recording
```

### Database Migration
```bash
python manage.py makemigrations cctv
python manage.py migrate cctv
```

## Configuration

### Camera Setup
1. Navigate to CCTV Settings
2. Click "Add Camera"
3. Enter camera details:
   - Name and location
   - IP address and port (default: 554 for RTSP)
   - Username and password
   - Select camera model

### Recording Schedule
- Set up automatic recording schedules
- Configure retention policies (default: 7 days)
- Enable motion-triggered recording

### Storage Configuration
- Default path: `/media/cctv/recordings`
- Automatic cleanup of old recordings
- Storage usage monitoring and alerts

## API Endpoints

### Camera Management
- `GET /api/v1/cctv/cameras/` - List all cameras
- `POST /api/v1/cctv/cameras/` - Add new camera
- `GET /api/v1/cctv/cameras/{id}/` - Get camera details
- `PUT /api/v1/cctv/cameras/{id}/` - Update camera
- `DELETE /api/v1/cctv/cameras/{id}/` - Delete camera

### Recording Control
- `POST /cctv/record/start/{camera_id}/` - Start recording
- `POST /cctv/record/stop/{camera_id}/` - Stop recording
- `GET /cctv/recordings/` - List recordings
- `GET /cctv/playback/{recording_id}/` - Playback recording

### Live Streaming
- `GET /cctv/stream/{camera_id}/` - MJPEG stream
- `GET /cctv/snapshot/{camera_id}/` - Current snapshot

### PTZ Control
- `GET /cctv/api/ptz/{camera_id}/?command={up|down|left|right|zoom_in|zoom_out|home}`

## Security Considerations

### Authentication
- All endpoints require user authentication
- Camera credentials are stored securely (encryption recommended for production)
- User-based access control for cameras and recordings

### Network Security
- RTSP streams use authentication
- HTTPS recommended for web interface
- Firewall rules for camera network isolation

## Future Enhancements

### Planned Features
1. **AI Integration**
   - Face recognition
   - License plate recognition
   - Object detection and tracking

2. **Advanced Recording**
   - H.265 codec support
   - Cloud storage integration
   - Bandwidth optimization

3. **Mobile Support**
   - Responsive mobile interface
   - Push notifications for alerts
   - Mobile app integration

4. **Analytics Dashboard**
   - Heat maps
   - Traffic patterns
   - Historical analytics

## Troubleshooting

### Common Issues

1. **No Signal from Camera**
   - Verify camera IP and port
   - Check network connectivity
   - Confirm RTSP credentials
   - Test with VLC: `vlc rtsp://username:password@ip:port/stream1`

2. **Recording Not Working**
   - Check storage permissions
   - Verify FFmpeg installation
   - Monitor disk space

3. **Stream Lag**
   - Reduce video quality settings
   - Check network bandwidth
   - Optimize camera bitrate

## TP-Link Tapo Camera URLs

### Default Endpoints
- Main Stream: `rtsp://username:password@ip:554/stream1`
- Sub Stream: `rtsp://username:password@ip:554/stream2`
- Snapshot: `http://username:password@ip/cgi-bin/snapshot.cgi`

### Tapo Account Setup
1. Use Tapo app to set up camera
2. Create local account (not cloud account)
3. Use local credentials in UNIBOS

## Kerberos.io Integration

### Setup
1. Deploy Kerberos.io instance
2. Configure camera in Kerberos
3. Enable Kerberos integration in UNIBOS
4. Enter Kerberos URL and API key

### Benefits
- Advanced motion detection
- Optimized recording
- Video analytics
- Reduced false positives

## License

Part of UNIBOS system - proprietary license.

## Support

For issues or questions, contact the UNIBOS development team.