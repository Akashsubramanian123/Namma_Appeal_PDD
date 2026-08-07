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
  // ── UPGRADED UNIVERSAL ROUTER WITH REGEX FALLBACK ──
  static Future<Map<String, dynamic>> getUniversalRoute(String userInput) async {
    final String systemPrompt = """
You are a strict routing system for a legal application. Your ONLY job is to read the user command and return the matching screen index number (0 to 7) and a clean payload.
- 0: Dashboard
- 1: Draft New RTI
- 2: Templates
- 3: Polish Existing Letter
- 4: Rejection Scanner
- 5: History & Tracking
- 6: Legal Co-Pilot
- 7: Profile

OUTPUT FORMAT MUST BE EXACTLY:
INDEX: [number]
PAYLOAD: [cleaned text or empty]
""";

    try {
      final response = await generateResponse(prompt: userInput, systemPrompt: systemPrompt);
      
      // Use RegEx to reliably extract the index number regardless of chatty text
      final indexRegExp = RegExp(r'INDEX:\s*([0-7])');
      final match = indexRegExp.firstMatch(response);
      
      int index = 6; // Default to Legal Co-Pilot (Chat)
      if (match != null) {
        index = int.parse(match.group(1)!);
      }

      // Extract Payload
      String payload = userInput;
      if (response.contains('PAYLOAD:')) {
        final parts = response.split('PAYLOAD:');
        if (parts.length > 1) {
          payload = parts[1].trim();
        }
      }
      
      return {'index': index, 'payload': payload.isEmpty ? userInput : payload};
    } catch (e) {
      return {'index': 6, 'payload': userInput}; 
    }
  }

  static Future<Map<String, dynamic>> getWorkspaceRoute(String userInput) async {
    final String systemPrompt = """
You are a workspace router for a legal app. Analyze the user text and categorize it into the correct screen index:
- 1: Draft New RTI (Use this if the user wants to file a new complaint, report a grievance, or describe a civic problem)
- 3: Polish Existing Letter (Use this if the user pasted a rough letter body, a draft, or text starting with 'To', 'Dear')
- 4: Rejection Scanner (Use this if the user mentions an RTI rejection, a rejected order, dismissal, or wanting to appeal a rejection like 'my rti got rejected')
- 6: Legal Co-Pilot (Use this ONLY if the user is asking a direct conversational question or legal doubt like 'What is section 8?')

OUTPUT FORMAT MUST BE EXACTLY:
INDEX: [1, 3, 4, or 6]
PAYLOAD: [cleaned text]
""";

    try {
      final response = await generateResponse(prompt: userInput, systemPrompt: systemPrompt);
      
      final indexRegExp = RegExp(r'INDEX:\s*([1346])');
      final match = indexRegExp.firstMatch(response);
      
      int index = 1; 
      if (match != null) {
        index = int.parse(match.group(1)!);
      }

      String payload = userInput;
      if (response.contains('PAYLOAD:')) {
        final parts = response.split('PAYLOAD:');
        if (parts.length > 1) {
          payload = parts[1].trim();
        }
      }
      
      return {'index': index, 'payload': payload.isEmpty ? userInput : payload};
    } catch (e) {
      return {'index': 1, 'payload': userInput}; 
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
      final String ocrApiUrl = 'https://namma-appeal-ml-engine.onrender.com/extract-text'; 

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