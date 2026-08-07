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
  // ── REAL OCR ENGINE (FASTAPI + TESSERACT) ──
  static Future<String> extractTextFromImage(Uint8List imageBytes) async {
    try {
      // 1. Convert directly to base64 (No need for magic byte checks anymore)
      final String base64Image = base64Encode(imageBytes);

      // 2. Point to your local Python backend (Update this to your Render URL for production)
      final String ocrApiUrl = 'http://127.0.0.1:8000/extract-text'; 

      final response = await http.post(
        Uri.parse(ocrApiUrl),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'base64_image': base64Image,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['extracted_text'].toString().trim();
      } else {
        throw Exception('OCR Engine error: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to connect to true OCR: $e');
    }
  }
}