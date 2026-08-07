import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'main.dart'; // Access themes and PremiumGlassCard
import 'local_llm_service.dart';
class PolisherScreen extends StatefulWidget {
  final Function(String)? onChatTriggered;
  final Function(int, [String?])? onNavigate;
  final String? initialText;

  const PolisherScreen({super.key, this.onChatTriggered, this.onNavigate, this.initialText});

  @override
  State<PolisherScreen> createState() => _PolisherScreenState();
}

class _PolisherScreenState extends State<PolisherScreen> {
  final TextEditingController _textController = TextEditingController();
  bool _isStreaming = false;
  String _polishedResult = "";

  @override
  void initState() {
    super.initState();
    if (widget.initialText != null) {
      _textController.text = widget.initialText!;
    }
  }

  Future<void> _processText() async {
    String textInput = _textController.text.trim();
    if (textInput.isEmpty) return;

    HapticFeedback.lightImpact();
    setState(() => _isStreaming = true);

    try {
      // 1. Run text through the workspace router
      final routeData = await LocalLLMService.getWorkspaceRoute(textInput);
      int targetIndex = routeData['index'];
      setState(() => _isStreaming = false);

      // 2. If it's a rejection/appeal -> Route to Rejection Scanner (Index 4)
      if (targetIndex == 4 && widget.onNavigate != null) {
        bool? confirmed = await _showRoutingConfirmation(context, "Rejection Scanner", textInput);
        if (confirmed == true && mounted) {
          _textController.clear();
          widget.onNavigate!(4);
        }
        return;
      }

      // 3. If it's a general question/doubt -> Route to Legal Co-Pilot (Index 6)
      if (targetIndex == 6 && widget.onNavigate != null) {
        bool? confirmed = await _showRoutingConfirmation(context, "Legal Co-Pilot", textInput);
        if (confirmed == true && mounted) {
          _textController.clear();
          widget.onNavigate!(6, textInput);
        }
        return;
      }

      // 4. If it's a new grievance -> Route to Draft New RTI (Index 1)
      if (targetIndex == 1 && widget.onNavigate != null) {
        bool? confirmed = await _showRoutingConfirmation(context, "Draft New RTI", textInput);
        if (confirmed == true && mounted) {
          _textController.clear();
          widget.onNavigate!(1, textInput);
        }
        return;
      }

      // 5. Otherwise, proceed with normal Polishing (Index 3)
      setState(() => _isStreaming = true);
      final profile = userProfileNotifier.value;
      String userName = profile != null && (profile['full_name'] ?? '').isNotEmpty 
          ? profile['full_name'] 
          : "an Indian citizen";

      final String systemInstruction = 
          "You are a helpful assistant rewriting a rough text into a clear, professional formal RTI application for $userName. "
          "CRITICAL: DO NOT pretend to be a lawyer. Write from a standard citizen's perspective. "
          "DO NOT add conversational filler. ONLY return the rewritten letter.";
      
      final polishedText = await LocalLLMService.generateResponse(
        prompt: textInput, 
        systemPrompt: systemInstruction
      );

      setState(() {
        _polishedResult = polishedText;
        _isStreaming = false;
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('✨ Letter professionally polished!'), backgroundColor: kSuccessEmerald),
        );
      }
    } catch (e) {
      setState(() => _isStreaming = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e'), backgroundColor: kRejectedRed));
      }
    }
  }

  // Helper for the popup confirmation box
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
          'Based on your text ("$reason"), our AI suggests routing you to the $destinationName screen to handle this properly.\n\nWould you like to proceed?',
          style: const TextStyle(color: kTextSecondary, fontSize: 14),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Stay Here', style: TextStyle(color: kTextSecondary)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: kRoyalBlue, foregroundColor: Colors.white),
            onPressed: () => Navigator.of(ctx).pop(true),
            child: const Text('Proceed'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final themeColor = Theme.of(context).colorScheme.primary;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("AI Document Polisher", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: kTextSlate)),
          const SizedBox(height: 8),
          const Text("Paste an existing rough letter or application here. Our legal AI will format it perfectly.", style: TextStyle(color: kTextSecondary)),
          const SizedBox(height: 24),

          PremiumGlassCard(
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                TextField(
                  controller: _textController,
                  maxLines: 8,
                  decoration: InputDecoration(
                    hintText: "To the PIO, I am writing to ask about the broken road...",
                    hintStyle: TextStyle(color: kTextSecondary.withOpacity(0.5)),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: Colors.black12)),
                    filled: true,
                    fillColor: Colors.white.withOpacity(0.5),
                  ),
                ),
                const SizedBox(height: 20),
                ElevatedButton.icon(
                  onPressed: _isStreaming ? null : _processText,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: themeColor,
                    foregroundColor: Colors.white,
                    minimumSize: const Size(double.infinity, 54),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  icon: _isStreaming ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2)) : const Icon(Icons.auto_fix_high),
                  label: Text(_isStreaming ? "Analyzing Intent..." : "Review & Polish Letter", style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                ),
              ],
            ),
          ),
          
          if (_polishedResult.isNotEmpty) ...[
            const SizedBox(height: 32),
            const Text("Polished Legal Draft", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: kTextSlate)),
            const SizedBox(height: 16),
            PremiumGlassCard(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  MarkdownBody(data: _polishedResult, selectable: true),
                  const SizedBox(height: 24),
                  OutlinedButton.icon(
                    onPressed: () => generateAndPrintPdf(_polishedResult, context, isAppeal: false),
                    style: OutlinedButton.styleFrom(minimumSize: const Size(double.infinity, 50)),
                    icon: const Icon(Icons.picture_as_pdf),
                    label: const Text("Generate PDF"),
                  ),
                ],
              ),
            ),
          ]
        ],
      ),
    );
  }
}