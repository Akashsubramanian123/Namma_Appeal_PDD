import 'dart:convert';
import 'package:http/http.dart' as http;

class MLEngineService {
  // ⚠️ REPLACE THIS with your actual Render Web Service URL
  static const String baseUrl = 'https://namma-appeal-ml-engine.onrender.com';

  static Future<double> getResponseTime(String department, String state, String section) async {
    final response = await http.post(
      Uri.parse('$baseUrl/predict-response-time'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'department': department,
        'state': state,
        'section': section,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['predicted_response_days'].toDouble();
    } else {
      throw Exception('Failed to fetch response time prediction from local ML Engine.');
    }
  }

  static Future<Map<String, dynamic>> getAppealOutcome(String rejectionReason, String department) async {
    final response = await http.post(
      Uri.parse('$baseUrl/predict-appeal-outcome'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'rejection_ground': rejectionReason,
        'department': department,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to fetch appeal outcome prediction from local ML Engine.');
    }
  }
}