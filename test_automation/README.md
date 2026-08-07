# Namma-Appeal Enterprise Test Automation, Security & Load Suite

Production-ready enterprise-grade E2E mobile automation, web functional, load performance stress, and OWASP security audit framework for the **Namma-Appeal** hybrid Flutter Android application, Python FastAPI OCR engine, local Ollama LLM, and Supabase PostgreSQL backend.

---

## Architecture & Test Suite Breakdown (400 Total Test Cases)

The framework is built in **JavaScript (Node.js)** with **Mocha / Chai**, **Appium 2.x**, **Selenium WebDriver / Playwright**, **k6**, **OWASP ZAP**, **ExcelJS**, and **Winston Logger**.

| Quadrant | Test Domain | Case Count | Tech Stack |
| :--- | :--- | :--- | :--- |
| **Quadrant 1** | Mobile Appium E2E & Flutter Widgets | 100 Cases | Appium 2.x, `@appium/flutter-driver`, UiAutomator2 |
| **Quadrant 2** | Web Selenium / Playwright Functional | 100 Cases | Selenium WebDriver / Playwright, Chrome/Firefox Headless |
| **Quadrant 3** | Load & Performance Stress Scenarios | 100 VUs | k6 / Axios Stress Runner, Ollama, FastAPI OCR, Supabase |
| **Quadrant 4** | Security & Vulnerability Scanning | 100 Checks | OWASP ZAP DAST, PII Gateway, RLS Bypass, JWT Audit |

---

## Directory Structure

```
test_automation/
├── package.json                   # Node.js dependencies & npm run scripts
├── runner.js                      # Master Test Orchestrator executing all 400 test cases
├── config/
│   └── config.js                  # Central configuration (Appium, Selenium, Endpoints, Timestamps)
├── utils/
│   ├── logger.js                  # Winston structured logging utility (console & file)
│   ├── excelReporter.js           # ExcelJS workbook generator for 7-sheet master report
│   ├── htmlReporter.js            # Mochawesome HTML master dashboard generator
│   └── failureHandler.js          # Failure capturer (Screenshots, stack traces, device logs)
├── pages/
│   ├── mobile/                    # Mobile Page Object Model (POM) classes
│   │   ├── authPage.js
│   │   ├── rejectionScannerPage.js
│   │   ├── rtiGeneratorPage.js
│   │   ├── chatPage.js
│   │   └── settingsPage.js
│   └── web/                       # Web Page Object Model (POM) classes
│       ├── dashboardPage.js
│       ├── searchRouterPage.js
│       └── webChatPage.js
├── tests/
│   ├── mobile/
│   │   └── appium_e2e.test.js     # 100 Mobile E2E Test Cases
│   ├── web/
│   │   └── selenium_functional.test.js # 100 Web Functional Test Cases
│   ├── load/
│   │   └── k6_stress_suite.js     # 100 Virtual User Load Scenarios
│   └── security/
│       └── security_audit.test.js # 100 Security & Vulnerability Checks
└── reports/
    ├── Namma_Appeal_Master_Enterprise_Report.xlsx  # Multi-sheet Excel Master Report
    ├── master-dashboard.html                       # HTML Master Dashboard
    └── failures/                                   # Failure Screenshots (.png)
```

---

## Prerequisites & Installation

1. **Node.js**: Ensure Node.js 18+ is installed (`node -v`).
2. **Appium 2.x**: Install Appium globally and the required drivers:
   ```bash
   npm install -g appium@next
   appium driver install uiautomator2
   appium driver install flutter
   ```
3. **Install Project Dependencies**:
   ```bash
   cd test_automation
   npm install
   ```

---

## Execution Commands

### 1. Run Complete 400-Case Master Suite
To execute all 4 quadrants sequentially and generate the Master Excel Report and HTML Dashboard:
```bash
npm test
# OR
node runner.js
```

### 2. Run Individual Quadrants
- **Mobile Appium Suite (100 Cases)**:
  ```bash
  npm run test:mobile
  ```
- **Web Selenium Suite (100 Cases)**:
  ```bash
  npm run test:web
  ```
- **Load & Performance Stress Suite (100 VUs)**:
  ```bash
  npm run test:load
  ```
- **Security & Vulnerability Audit (100 Checks)**:
  ```bash
  npm run test:security
  ```

---

## Master Excel Report (`Namma_Appeal_Master_Enterprise_Report.xlsx`)

The framework generates a 7-sheet master workbook styled with corporate palettes:
- **Sheet 1 - Executive Summary**: KPI overview cards, pass percentage, execution duration, environment metadata.
- **Sheet 2 - Mobile Appium Results**: 100 rows with Test ID, Module, Scenario Name, Status, Device Info, Duration.
- **Sheet 3 - Web Selenium Results**: 100 rows with Test ID, Page Target, User Action, Status, Browser, Duration.
- **Sheet 4 - Load Testing Metrics**: 100 rows with Scenario Name, VUs, RPS, p95 Latency, Error Rate.
- **Sheet 5 - Security Audit**: 100 rows with Check ID, Category, Severity, Status, Remediation Notes.
- **Sheet 6 - Failed Tests**: Detailed failure breakdown with stack traces and screenshot file paths.
- **Sheet 7 - Execution Logs**: Timestamped execution log steps.

---

## CI/CD Pipeline Integration

The framework includes GitHub Actions workflows configured in `.github/workflows/flutter-enterprise-suite.yml`.
On push to `main` or `develop`, the workflow:
1. Provisions Java JDK 17, Node.js 20, and Android SDK (API 34).
2. Spawns an Android Emulator.
3. Builds release APK (`app-release.apk`).
4. Runs all 400 test cases via `runner.js`.
5. Uploads `Namma_Appeal_Master_Enterprise_Report.xlsx` and `master-dashboard.html` as downloadable artifacts.
