import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'earthquake_list_screen.dart';
import 'earthquake_map_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const EarthquakeListScreen(),
    const EarthquakeMapScreen(),
    const SettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          border: Border(
            top: BorderSide(color: Color(0xFF00ff00), width: 1),
          ),
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) {
            setState(() {
              _currentIndex = index;
            });
          },
          backgroundColor: const Color(0xFF0a0a0a),
          selectedItemColor: const Color(0xFF00ff00),
          unselectedItemColor: const Color(0xFF666666),
          selectedLabelStyle: const TextStyle(
            fontFamily: 'CourierNew',
            fontSize: 10,
          ),
          unselectedLabelStyle: const TextStyle(
            fontFamily: 'CourierNew',
            fontSize: 10,
          ),
          type: BottomNavigationBarType.fixed,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.list),
              label: 'depremler',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.map),
              label: 'harita',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.settings),
              label: 'ayarlar',
            ),
          ],
        ),
      ),
    );
  }
}
