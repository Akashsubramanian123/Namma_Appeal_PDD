import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'ml_engine_service.dart';
import 'local_llm_service.dart';
import 'main.dart'; // For generateAndPrintPdf

class ScannerScreen extends StatefulWidget {
  final Function(String)? onChatTriggered;

  const ScannerScreen({super.key, this.onChatTriggered});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  Uint8List? _imageBytes;
  String _scannedText = '';
  String _generatedAppeal = '';
  Map<String, dynamic>? _predictionResult;
  bool _isProcessing = false;
  bool _isGeneratingAppeal = false;
  
  final ImagePicker _picker = ImagePicker();

  Future<void> _pickAndScanImage(ImageSource source) async {
    try {
      final pickedFile = await _picker.pickImage(source: source);
      if (pickedFile == null) return;

      final bytes = await pickedFile.readAsBytes();

      setState(() {
        _imageBytes = bytes;
        _isProcessing = true;
        _scannedText = '';
        _generatedAppeal = '';
        _predictionResult = null;
      });

      String extractedText = "";

      if (!kIsWeb) {
        final inputImage = InputImage.fromFilePath(pickedFile.path);
        final textRecognizer = TextRecognizer(script: TextRecognitionScript.latin);
        final RecognizedText recognizedText = await textRecognizer.processImage(inputImage);
        await textRecognizer.close();
        extractedText = recognizedText.text;
      } else {
        setState(() => _scannedText = "Running AI Vision OCR...");
        extractedText = await LocalLLMService.extractTextFromImage(bytes);
      }

      // Fetch ML Prediction from Render Backend
      Map<String, dynamic>? mlPrediction;
      if (extractedText.isNotEmpty) {
        try {
          mlPrediction = await MLEngineService.getAppealOutcome(
            extractedText,
            "General Department",
          );
        } catch (e) {
          // Store the error so a helpful debug card renders on screen
          mlPrediction = {
            'error': true,
            'message': '$e',
          };
        }
      }

      setState(() {
        _scannedText = extractedText.isEmpty ? "No text found in document." : extractedText;
        _predictionResult = mlPrediction;
        _isProcessing = false;
      });

    } catch (e) {
      setState(() {
        _isProcessing = false;
        _scannedText = "Error scanning document: $e";
      });
    }
  }

  // ── GENERATE FIRST APPEAL VIA LOCAL LLAMA 3 ──
  Future<void> _generateFirstAppeal() async {
    if (_scannedText.isEmpty) return;

    setState(() => _isGeneratingAppeal = true);

    try {
      const String systemInstruction = 
          "You are a senior Indian High Court lawyer and RTI expert. "
          "Analyze the provided RTI rejection text and draft a complete, formal First Appeal under Section 19(1) of the Right to Information Act, 2005. "
          "Cite relevant sections of the RTI Act to counter the rejection ground. "
          "Write a continuous formal letter. End completely with: [END OF DRAFT].";

      final String prompt = "Rejection Order Text:\n$_scannedText\n\nDraft a formal First Appeal letter against this rejection.";

      final String appealDraft = await LocalLLMService.generateResponse(
        prompt: prompt,
        systemPrompt: systemInstruction,
      );

      setState(() {
        _generatedAppeal = appealDraft;
        _isGeneratingAppeal = false;
      });
    } catch (e) {
      setState(() {
        _isGeneratingAppeal = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error drafting appeal: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Offline Document Scanner'),
        backgroundColor: Colors.blueGrey[900],
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Image Preview Area
            Container(
              height: 250,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.grey.shade400),
              ),
              child: _imageBytes != null
                  ? ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: Image.memory(_imageBytes!, fit: BoxFit.cover),
                    )
                  : const Center(
                      child: Text(
                        'No Document Selected',
                        style: TextStyle(color: Colors.grey),
                      ),
                    ),
            ),
            const SizedBox(height: 20),

            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton.icon(
                  onPressed: _isProcessing ? null : () => _pickAndScanImage(ImageSource.camera),
                  icon: const Icon(Icons.camera_alt),
                  label: const Text('Camera'),
                ),
                ElevatedButton.icon(
                  onPressed: _isProcessing ? null : () => _pickAndScanImage(ImageSource.gallery),
                  icon: const Icon(Icons.photo_library),
                  label: const Text('Gallery'),
                ),
              ],
            ),
            const SizedBox(height: 24),

            if (_isProcessing)
              const Center(
                child: Column(
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 12),
                    Text('Running Document OCR & ML Prediction...'),
                  ],
                ),
              ),

            // ML Adjudication Prediction Card
            // ML Adjudication Prediction Card
            if (!_isProcessing && _predictionResult != null)
              Card(
                color: _predictionResult!['error'] == true ? Colors.orange.shade50 : Colors.green.shade50,
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: _predictionResult!['error'] == true
                      ? Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              '⚠️ ML Predictor Status',
                              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.orange),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              '${_predictionResult!['message']}',
                              style: const TextStyle(fontSize: 12),
                            ),
                          ],
                        )
                      : Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              '🧠 ML Adjudication Prediction',
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                            ),
                            const Divider(),
                            Text(
                              'Outcome: ${_predictionResult!['predicted_outcome']}',
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                            ),
                            const SizedBox(height: 8),
                            Text('Win Probability: ${_predictionResult!['win_probability_percent']}%'),
                            const SizedBox(height: 8),
                            Text('Recommendation: ${_predictionResult!['recommended_action']}'),
                          ],
                        ),
                ),
              ),
            const SizedBox(height: 16),

            // Extracted Text
            if (!_isProcessing && _scannedText.isNotEmpty) ...[
              const Text(
                'Extracted Text:',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: Text(
                  _scannedText,
                  style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
                ),
              ),
              const SizedBox(height: 20),

              // Button to draft First Appeal
              ElevatedButton.icon(
                onPressed: _isGeneratingAppeal ? null : _generateFirstAppeal,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2563EB),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                icon: _isGeneratingAppeal 
                    ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                    : const Icon(Icons.gavel),
                label: Text(
                  _isGeneratingAppeal ? "Drafting First Appeal via Local AI..." : "Generate First Appeal Letter",
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
            ],

            // Display Generated First Appeal Draft
            if (_generatedAppeal.isNotEmpty) ...[
              const SizedBox(height: 24),
              const Text(
                'Generated First Appeal Letter:',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.blue.shade200),
                ),
                child: MarkdownBody(data: _generatedAppeal, selectable: true),
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () => generateAndPrintPdf(_generatedAppeal, context, isAppeal: true),
                icon: const Icon(Icons.picture_as_pdf),
                label: const Text("Generate Appeal PDF"),
              ),
            ],
          ],
        ),
      ),
    );
  }
}