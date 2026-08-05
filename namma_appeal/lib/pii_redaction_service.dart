class PIIRedactionService {
  // Regex Patterns for Indian PII
  static final RegExp _aadhaarRegex = RegExp(
    r'\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b',
  );

  static final RegExp _phoneRegex = RegExp(
    r'\b(?:\+?91[\-\s]?)?[6-9]\d{9}\b',
  );

  static final RegExp _emailRegex = RegExp(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
  );

  static final RegExp _panRegex = RegExp(
    r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
    caseSensitive: false,
  );

  static final RegExp _creditCardRegex = RegExp(
    r'\b(?:\d[ -]*?){13,16}\b',
  );

  /// Sanitizes text by stripping all identified PII before LLM processing
  static String sanitize(String input) {
    if (input.isEmpty) return input;

    String sanitized = input;

    // 1. Redact Aadhaar Numbers
    sanitized = sanitized.replaceAllMapped(_aadhaarRegex, (match) {
      return '[AADHAAR_REDACTED]';
    });

    // 2. Redact Phone Numbers
    sanitized = sanitized.replaceAllMapped(_phoneRegex, (match) {
      return '[PHONE_REDACTED]';
    });

    // 3. Redact Email Addresses
    sanitized = sanitized.replaceAllMapped(_emailRegex, (match) {
      return '[EMAIL_REDACTED]';
    });

    // 4. Redact PAN Card Numbers
    sanitized = sanitized.replaceAllMapped(_panRegex, (match) {
      return '[PAN_REDACTED]';
    });

    // 5. Redact Financial Card / Account Numbers
    sanitized = sanitized.replaceAllMapped(_creditCardRegex, (match) {
      return '[FINANCIAL_DATA_REDACTED]';
    });

    return sanitized;
  }
}