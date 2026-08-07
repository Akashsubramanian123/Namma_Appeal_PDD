const path = require('path');
require('dotenv').config();

module.exports = {
  appName: 'Namma-Appeal Enterprise Automation Suite',
  version: '1.0.0',
  environment: process.env.TEST_ENV || 'staging',
  baseUrl: process.env.BASE_URL || 'http://localhost:3000',

  // Quadrant 1: Appium & Flutter Mobile Config
  appium: {
    host: process.env.APPIUM_HOST || '127.0.0.1',
    port: parseInt(process.env.APPIUM_PORT || '4723', 10),
    capabilities: {
      platformName: 'Android',
      'appium:automationName': 'flutter', // Fallback to UiAutomator2 if needed
      'appium:deviceName': process.env.ANDROID_DEVICE_NAME || 'Android_Emulator_API_34',
      'appium:app': process.env.APK_PATH || path.resolve(__dirname, '../../namma_appeal/build/app/outputs/flutter-apk/app-release.apk'),
      'appium:appPackage': 'com.namma.appeal.namma_appeal',
      'appium:appActivity': '.MainActivity',
      'appium:noReset': false,
      'appium:fullReset': false,
      'appium:newCommandTimeout': 300
    }
  },

  // Quadrant 2: Selenium / Playwright Web Config
  web: {
    browser: process.env.BROWSER || 'chrome', // chrome | firefox | edge
    headless: process.env.HEADLESS === 'true' || false,
    viewports: [
      { name: 'Desktop Ultra', width: 1920, height: 1080 },
      { name: 'Desktop Standard', width: 1440, height: 900 },
      { name: 'Laptop', width: 1280, height: 800 },
      { name: 'Tablet Landscape', width: 1024, height: 768 },
      { name: 'Tablet Portrait', width: 768, height: 1024 },
      { name: 'Mobile Web', width: 375, height: 812 }
    ],
    implicitWaitMs: 10000,
    pageLoadTimeoutMs: 30000
  },

  // Quadrant 3: Load Testing Endpoints
  endpoints: {
    ollama: process.env.OLLAMA_URL || 'http://127.0.0.1:11434',
    fastApiOcr: process.env.FASTAPI_OCR_URL || 'http://127.0.0.1:8000',
    supabaseUrl: process.env.SUPABASE_URL || 'https://mock-supabase-project.supabase.co',
    supabaseAnonKey: process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_key'
  },

  // Quadrant 4: Security Thresholds
  security: {
    zapApiUrl: process.env.ZAP_API_URL || 'http://127.0.0.1:8080',
    zapApiKey: process.env.ZAP_API_KEY || 'zap_enterprise_secret_123',
    strictPiiMasking: true,
    enforceRls: true
  },

  // Report Directories
  reports: {
    outputDir: path.resolve(__dirname, '../reports'),
    failuresDir: path.resolve(__dirname, '../reports/failures'),
    logsDir: path.resolve(__dirname, '../logs'),
    masterExcelFile: path.resolve(__dirname, '../reports/Namma_Appeal_Master_Enterprise_Report.xlsx'),
    masterHtmlDashboard: path.resolve(__dirname, '../reports/master-dashboard.html')
  }
};
