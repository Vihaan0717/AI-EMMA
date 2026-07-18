import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;

void main() => runApp(const NexusApp());

// --- CONFIGURATION ---
const String CLIENT_ID = "mobile_command";

// Default fallback — only used on first launch
// Change this to your Cloudflare URL via the Settings screen (gear icon)
// NOTE: This is a trycloudflare.com URL — it changes each time the tunnel restarts.
// Update it in ⚙️ Settings or change this constant and rebuild.
const String DEFAULT_BRIDGE_URL = "prerequisite-discrimination-territory-liberty.trycloudflare.com";

class NexusApp extends StatelessWidget {
  const NexusApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'NEXUS-X Command',
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF0A0A0F),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF00FFD1),
          secondary: Color(0xFFA855F7),
        ),
      ),
      home: const WarRoomScreen(),
    );
  }
}

// ─────────────────────────────────────────────
// SETTINGS SCREEN
// ─────────────────────────────────────────────
class SettingsScreen extends StatefulWidget {
  final String currentUrl;
  const SettingsScreen({super.key, required this.currentUrl});
  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late TextEditingController _urlController;

  @override
  void initState() {
    super.initState();
    _urlController = TextEditingController(text: widget.currentUrl);
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    final raw = _urlController.text.trim();
    // Strip any leading ws:// wss:// http:// https:// — we handle scheme ourselves
    final cleaned = raw
        .replaceAll(RegExp(r'^wss?://'), '')
        .replaceAll(RegExp(r'^https?://'), '');
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('bridge_url', cleaned);
    if (mounted) Navigator.pop(context, cleaned);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0D0D1A),
        title: const Text('⚙️ Zero Protocol Settings',
            style: TextStyle(color: Color(0xFF00FFD1), fontSize: 15)),
        iconTheme: const IconThemeData(color: Color(0xFF00FFD1)),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Card: Cloudflare URL
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: const Color(0xFF131325),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFF00FFD1).withOpacity(0.2)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('🌐 Bridge URL',
                      style: TextStyle(
                          color: Color(0xFF00FFD1),
                          fontWeight: FontWeight.bold,
                          fontSize: 14)),
                  const SizedBox(height: 8),
                  const Text(
                    'Enter your Cloudflare tunnel URL (e.g. abc-xyz.trycloudflare.com)\n'
                    'or your local IP+port (e.g. 192.168.0.103:8000).\n\n'
                    'Do NOT include http:// or ws:// — the app handles that.',
                    style: TextStyle(color: Colors.white54, fontSize: 12, height: 1.5),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _urlController,
                    style: const TextStyle(color: Colors.white, fontFamily: 'monospace'),
                    decoration: InputDecoration(
                      hintText: 'abc-xyz.trycloudflare.com',
                      hintStyle: const TextStyle(color: Colors.white24),
                      filled: true,
                      fillColor: const Color(0xFF0A0A0F),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(color: Color(0xFF00FFD1), width: 0.5),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(
                            color: const Color(0xFF00FFD1).withOpacity(0.3), width: 0.5),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(color: Color(0xFF00FFD1), width: 1),
                      ),
                      contentPadding:
                          const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                    ),
                    autocorrect: false,
                    keyboardType: TextInputType.url,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            // Info box
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF0D1A0D),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                    color: Colors.greenAccent.withOpacity(0.2), width: 0.5),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('💡 How to get your Cloudflare URL',
                      style: TextStyle(
                          color: Colors.greenAccent,
                          fontWeight: FontWeight.bold,
                          fontSize: 13)),
                  SizedBox(height: 8),
                  Text(
                    '1. Double-click Launch_Zero.bat on your desktop\n'
                    '2. A tunnel window opens automatically\n'
                    '3. Look for the line:\n'
                    '   │  https://abc-xyz.trycloudflare.com\n'
                    '4. Copy that URL (without https://) and paste here',
                    style: TextStyle(
                        color: Colors.white54, fontSize: 12, height: 1.6),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _save,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF00FFD1),
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
             // --- MINIMALIST ASSIST BALL UI ---
class WarRoomScreen extends StatefulWidget {
  const WarRoomScreen({super.key});
  @override
  State<WarRoomScreen> createState() => _WarRoomScreenState();
}

class _WarRoomScreenState extends State<WarRoomScreen> with WidgetsBindingObserver {
  String _bridgeUrl = DEFAULT_BRIDGE_URL;
  WebSocketChannel? _channel;
  bool _isConnected = false;
  bool _isMenuOpen = false;
  
  // Mock data for Assist Ball
  Map<String, dynamic> _status = {"node": "ONLINE", "agents": "3 ACTIVE"};
  List<String> _news = ["NEXUS-X Intelligence Upgrade Complete", "AI Policy updated in Hyderabad"];
  
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _loadUrlAndConnect();
  }

  Future<void> _loadUrlAndConnect() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() => _bridgeUrl = prefs.getString('bridge_url') ?? DEFAULT_BRIDGE_URL);
    _connect();
  }

  void _connect() {
    final uri = Uri.parse("wss://$_bridgeUrl/ws/nexus");
    try {
      _channel = WebSocketChannel.connect(uri);
      setState(() => _isConnected = true);
    } catch (e) {
      setState(() => _isConnected = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black, // PURE BLACK BACKGROUND
      body: Stack(
        children: [
          // 1. MAIN AGENT STATUS (Floating Text)
          Positioned(
            top: 60,
            left: 20,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("NEXUS BRAIN: ${_status['node']}", 
                  style: const TextStyle(color: Color(0xFF00FFD1), fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 2)),
                const SizedBox(height: 5),
                Text("FLEET: ${_status['agents']}", 
                  style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 10)),
              ],
            ),
          ),

          // 2. THE ASSIST BALL (Floating Action Button)
          Align(
            alignment: Alignment.center,
            child: GestureDetector(
              onTap: () => setState(() => _isMenuOpen = !_isMenuOpen),
              child: Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.black,
                  border: Border.all(color: const Color(0xFF00FFD1), width: 2),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF00FFD1).withOpacity(0.3),
                      blurRadius: 20,
                      spreadRadius: 5,
                    )
                  ],
                ),
                child: const Center(
                  child: Icon(Icons.bolt, color: Color(0xFF00FFD1), size: 30),
                ),
              ),
            ),
          ),

          // 3. EXPANDABLE MENU (Hiding News/Movies/Weather)
          if (_isMenuOpen)
            Positioned.fill(
              child: GestureDetector(
                onTap: () => setState(() => _isMenuOpen = false),
                child: Container(
                  color: Colors.black.withOpacity(0.8),
                  child: Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        _menuItem("📰 NEWS", () {}),
                        _menuItem("🎬 MOVIES", () {}),
                        _menuItem("☀️ WEATHER", () {}),
                        _menuItem("⚙️ SETTINGS", () {}),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            
          // 4. WAKE WORD LISTENER (Visual Indicator)
          Positioned(
            bottom: 40,
            left: 0,
            right: 0,
            child: Center(
              child: Text("LISTENING FOR 'JARVIS'...", 
                style: TextStyle(color: Colors.white.withOpacity(0.2), fontSize: 10, letterSpacing: 4)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _menuItem(String label, VoidCallback onTap) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 15),
      child: InkWell(
        onTap: onTap,
        child: Text(label, 
          style: const TextStyle(color: Color(0xFF00FFD1), fontSize: 18, fontWeight: FontWeight.w300, letterSpacing: 3)),
      ),
    );
  }
}
ed: (_) => _sendMessage(),
              ),
            ),
          ),
          const SizedBox(width: 8),
          CircleAvatar(
            backgroundColor: _isRecording ? Colors.redAccent : const Color(0xFF00FFD1),
            radius: 22,
            child: IconButton(
                icon: Icon(_isRecording ? Icons.stop : Icons.mic, color: Colors.black),
                onPressed: _toggleRecording),
          ),
        ],
      ),
    );
  }
}