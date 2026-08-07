import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'ml_engine_service.dart';
import 'local_llm_service.dart';
import 'main.dart'; 
import 'reminder_service.dart'; 

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
  String _fullAiResponse = ''; 
  Map<String, dynamic>? _predictionResult;
  bool _isProcessing = false;
  bool _isGeneratingAppeal = false;
  
  final ImagePicker _picker = ImagePicker();

  Future<void> _offerRtiReminder(String draft, String topic, String targetRecordId) async {
    DateTime? filingDate = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime.now().subtract(const Duration(days: 30)),
      lastDate: DateTime.now().add(const Duration(days: 30)),
      helpText: 'Did you file this First Appeal? Pick the filing date to set reminders.',
      confirmText: 'Set Reminders',
      cancelText: 'Skip',
    );

    if (filingDate == null || !mounted) return;

    try {
      final ids = await ReminderService.scheduleRtiReminders(
        filingDate: filingDate,
        department: 'the concerned appellate authority',
        topic: topic,
      );

      await Supabase.instance.client.from('scan_history').update({
        'filing_date': filingDate.toIso8601String(),
        'notification_ids': ids,
      }).eq('id', targetRecordId);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('✅ Reminders set for Day 27 and Day 57!'), backgroundColor: Colors.green),
        );
      }
    } catch (e) {
      debugPrint('Reminder error: $e');
    }
  }

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
        _fullAiResponse = ''; 
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

      Map<String, dynamic>? mlPrediction;
      if (extractedText.isNotEmpty) {
        try {
          mlPrediction = await MLEngineService.getAppealOutcome(
            extractedText,
            "General Department",
          );
        } catch (e) {
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

  // ── GENERATE FIRST APPEAL VIA LOCAL LLAMA 3 (ML LOGIC + RAG) ──
  Future<void> _generateFirstAppeal() async {
    if (_scannedText.isEmpty) return;

    setState(() => _isGeneratingAppeal = true);

    try {
      final profile = userProfileNotifier.value;
      String userName = "an Indian citizen";
      String userAddress = "Address not provided";
      
      if (profile != null && (profile['full_name'] ?? '').isNotEmpty) {
        userName = profile['full_name'];
        userAddress = "${profile['address'] ?? ''}\nMobile: ${profile['mobile_number'] ?? ''}";
      }

      final String currentDate = "${DateTime.now().day}/${DateTime.now().month}/${DateTime.now().year}";

      // ── STEP 1: ML Validity Warning (Soft Block) ──
      String warningHeader = "";
      if (_predictionResult != null && 
          _predictionResult!['error'] != true && 
          _predictionResult!['win_probability_percent'] != null) {
          
          int winProbability = _predictionResult!['win_probability_percent'] as int;
          
          // Only show warning if ML predicts a low chance of winning (Valid PIO Rejection)
          if (winProbability < 40) {
             warningHeader = "### ⚠️ Weak Case Warning\n\n"
                             "**The ML Adjudication Engine predicts a $winProbability% chance of winning this appeal.** "
                             "This rejection likely falls under valid RTI exemptions. We have generated the draft below so you can exercise your right to appeal, but please review it carefully as the Appellate Authority may uphold the rejection.\n\n---\n\n";
          }
      }

      // ── STEP 2: Extract Topic for RAG ──
      final String topicPrompt = "Analyze this text and output ONLY the ONE-WORD legal topic (e.g., Language, Privacy, Security, Fee, Transfer, General):\n\n$_scannedText";
      String topic = await LocalLLMService.generateResponse(
        prompt: topicPrompt,
        systemPrompt: "You are a strict routing AI. Output only a single word.",
      );
      topic = topic.trim();

      // ── STEP 3: Retrieve Law Context from Supabase ──
      String lawContext = "";
      try {
        final response = await Supabase.instance.client
            .from('rti_laws')
            .select('content')
            .ilike('content', '%$topic%')
            .limit(3);
        
        final List<dynamic> laws = response as List<dynamic>;
        if (laws.isNotEmpty) {
          lawContext = laws.map((e) => e['content'].toString()).join("\n\n");
        } else {
          lawContext = "The RTI Act mandates transparency and requires public authorities to provide information unless strictly exempted under Section 8 or 9.";
        }
      } catch (dbError) {
        lawContext = "The RTI Act mandates transparency and requires public authorities to provide information.";
      }

      // ── STEP 4: Generate Draft using Law Context + Strict Template ──
      final String systemInstruction = 
          "You are drafting a First Appeal under Section 19(1) of the RTI Act on behalf of $userName.\n"
          "LEGAL CONTEXT TO USE:\n$lawContext\n\n"
          "STRICT RULES:\n"
          "1. Extract department name and address from the text. DO NOT leave bracketed placeholders like '[Insert Address]'. If address is missing, write 'The Concerned Public Authority'.\n"
          "2. Ensure 'To:' and 'From:' sections are separated clearly by blank lines.\n"
          "3. DO NOT write the word 'STOP' anywhere in your response.\n"
          "4. DO NOT write 'Thanking you', 'Yours faithfully', or any signature at the bottom.\n"
          "5. End your response immediately after point 2 of the relief requested.\n"
          "6. Write strictly in the first-person ('I', 'my'). Do NOT refer to the sender in the third-person as 'the applicant'.\n\n"
          "TEMPLATE TO FOLLOW:\n"
          "To,\n"
          "The First Appellate Authority,\n"
          "[Extracted Department Name and Address]\n\n"
          "From,\n"
          "$userName\n"
          "$userAddress\n\n"
          "Date: $currentDate\n\n"
          "Subject: First Appeal under Section 19(1) of the Right to Information Act, 2005 against improper rejection.\n\n"
          "Reference: Rejection order dated [Date from text] bearing No. [Order No from text].\n\n"
          "Dear Sir/Madam,\n\n"
          "I had submitted an application seeking information under the Right to Information Act, 2005.\n\n"
          "The Public Information Officer (PIO) responded with a rejection order stating: [Exact short quote/summary of rejection reason].\n\n"
          "I submit that the rejection order issued by the PIO is illegal, arbitrary, and directly contrary to the RTI Act, 2005. [Vigorously argue why the rejection is invalid using the provided LEGAL CONTEXT].\n\n"
          "Therefore, I humbly request you, as the First Appellate Authority, to:\n"
          "1. Set aside the improper rejection order.\n"
          "2. Direct the PIO to provide the requested information immediately.";

      final String prompt = "Rejection Order Text:\n$_scannedText\n\nDraft the appeal following the template.";

      String appealDraft = await LocalLLMService.generateResponse(
        prompt: prompt,
        systemPrompt: systemInstruction,
      );

      // ── STEP 5: Aggressive RegEx Cleanup ──
      appealDraft = appealDraft.replaceAll(RegExp(r'\[END OF DRAFT\]', caseSensitive: false), '');
      appealDraft = appealDraft.replaceAll(RegExp(r'^(here is the.*?draft.*?:|certainly!.*?:\n|sure,.*?:\n)\s*', multiLine: true, caseSensitive: false), '');
      appealDraft = appealDraft.replaceAll(RegExp(r'\n\s*STOP\s*$', caseSensitive: false), '');
      appealDraft = appealDraft.replaceAll(RegExp(r'\bSTOP\b', caseSensitive: false), '');
      appealDraft = appealDraft.trim();
      
      // Prepend the warning (if applicable based on ML score)
      appealDraft = warningHeader + appealDraft;

      // ── STEP 6: Save to Database & Show Reminder ──
      String generatedId = "";
      try {
        final insertedRow = await Supabase.instance.client.from('scan_history').insert({
          'topic': 'Appeal: $topic',
          'analysis_summary': 'First Appeal Draft against Rejection',
          'full_draft': appealDraft,
          'user_id': Supabase.instance.client.auth.currentUser?.id,
        }).select('id').single(); 
        generatedId = insertedRow['id'].toString();
      } catch (dbError) {
        debugPrint("Failed to save draft to database: $dbError");
      }

      setState(() {
        _generatedAppeal = appealDraft;
        _fullAiResponse = appealDraft; 
        _isGeneratingAppeal = false;
      });

      if (mounted && generatedId.isNotEmpty) {
         _offerRtiReminder(appealDraft, 'Appeal: $topic', generatedId);
      }

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
  Future<bool?> _showRoutingConfirmation(BuildContext context, String destinationName, String reason) async {
    return showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            const Icon(Icons.auto_awesome, color: kRoyalBlue),
            const SizedBox(width: 10),
            Text('Smart Routing: $destinationName', style: const TextStyle(color: kTextSlate, fontSize: 16, fontWeight: FontWeight.bold)),
          ],
        ),
        content: Text(
          'Based on your text ("$reason"), our AI suggests routing you to the $destinationName screen to complete this task properly.\n\nWould you like to proceed?',
          style: const TextStyle(color: kTextSecondary, fontSize: 14),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false), // Cancel
            child: const Text('Stay Here', style: TextStyle(color: kTextSecondary)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: kRoyalBlue, foregroundColor: Colors.white),
            onPressed: () => Navigator.of(ctx).pop(true), // Confirm
            child: const Text('Proceed'),
          ),
        ],
      ),
    );
  }
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      floatingActionButton: _fullAiResponse.isNotEmpty && !_isGeneratingAppeal
          ? FloatingActionButton.extended(
              onPressed: () {
                if (widget.onChatTriggered != null) {
                  widget.onChatTriggered!(_fullAiResponse);
                }
              },
              icon: const Icon(Icons.chat),
              label: const Text("Discuss Draft"),
              backgroundColor: const Color(0xFF2563EB),
              foregroundColor: Colors.white,
            )
          : null,
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
                onPressed: () {
                  // ── STRIP THE UI WARNING BEFORE PRINTING ──
                  String cleanDraft = _generatedAppeal;
                  if (cleanDraft.contains('---\n\n')) {
                    cleanDraft = cleanDraft.split('---\n\n').last.trim();
                  }
                  generateAndPrintPdf(cleanDraft, context, isAppeal: true);
                },
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