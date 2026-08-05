import 'dart:typed_data';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart' show kIsWeb, defaultTargetPlatform, TargetPlatform;
import 'pii_redaction_service.dart'; 

class LocalLLMService {
  static const String modelName = 'llama3'; 

  // ── SMART ROUTING: Auto-detects Web vs Phone ──
  static String get ollamaBaseUrl {
    if (kIsWeb) {
      return 'http://127.0.0.1:11434/api/generate'; // Web Browser Localhost
    } else if (defaultTargetPlatform == TargetPlatform.android) {
      return 'http://192.168.29.96:11434/api/generate'; // Android Emulator Localhost
    } else {
      return 'http://127.0.0.1:11434/api/generate'; // iOS Simulator / Windows Desktop
    }
  }

  static Future<String> generateResponse({required String prompt, required String systemPrompt}) async {
    try {
      // Pass prompt through the PII Redaction Gateway
      final String safePrompt = PIIRedactionService.sanitize(prompt);

      final response = await http.post(
        Uri.parse(ollamaBaseUrl),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'model': modelName,
          'system': systemPrompt,
          'prompt': safePrompt,
          'stream': false, 
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['response'];
      } else {
        throw Exception('Local Ollama server returned status code: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to connect to Local LLM: $e\nEnsure Ollama is running in your terminal.');
    }
  }
  // ── LOCAL VISION AI (WEB OCR FALLBACK) ──
  static Future<String> extractTextFromImage(Uint8List imageBytes) async {
    try {
      final String base64Image = base64Encode(imageBytes);

      final response = await http.post(
        Uri.parse(ollamaBaseUrl),
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true', 
        },
        body: jsonEncode({
          'model': 'llava', // ── Targets the Vision Model ──
          'prompt': 'You are an expert OCR system. Extract and transcribe all text from the provided document image accurately. Output strictly the extracted text and nothing else.',
          'images': [base64Image],
          'stream': false, 
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['response'].toString().trim();
      } else {
        throw Exception('Ollama Vision server returned status code: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to connect to Vision AI: $e');
    }
  }
}