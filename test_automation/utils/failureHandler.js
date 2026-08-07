const fs = require('fs');
const path = require('path');
const config = require('../config/config');
const logger = require('./logger');

class FailureHandler {
  static async handleFailure(driver, testName, error, suiteName = 'General') {
    logger.error(`[FAILURE DETECTED] Test: "${testName}" in Suite: "${suiteName}"`);
    logger.error(`Error Message: ${error.message}`);
    logger.error(`Stack Trace:\n${error.stack}`);

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const sanitizedTestName = testName.replace(/[^a-zA-Z0-9_-]/g, '_');
    const screenshotFileName = `FAIL_${suiteName}_${sanitizedTestName}_${timestamp}.png`;
    const screenshotPath = path.join(config.reports.failuresDir, screenshotFileName);

    if (!fs.existsSync(config.reports.failuresDir)) {
      fs.mkdirSync(config.reports.failuresDir, { recursive: true });
    }

    let capturedScreenshotPath = 'N/A';

    try {
      if (driver && typeof driver.takeScreenshot === 'function') {
        const imageBuffer = await driver.takeScreenshot();
        fs.writeFileSync(screenshotPath, Buffer.from(imageBuffer, 'base64'));
        capturedScreenshotPath = screenshotPath;
        logger.info(`Failure screenshot captured successfully: ${screenshotPath}`);
      } else if (driver && typeof driver.saveScreenshot === 'function') {
        await driver.saveScreenshot(screenshotPath);
        capturedScreenshotPath = screenshotPath;
        logger.info(`Failure screenshot captured successfully: ${screenshotPath}`);
      } else {
        logger.warn('Driver does not support screenshot capture capability.');
      }
    } catch (shotError) {
      logger.error(`Failed to capture screenshot during failure handling: ${shotError.message}`);
    }

    return {
      testName,
      suiteName,
      reason: error.message,
      stackTrace: error.stack,
      screenshotPath: capturedScreenshotPath,
      timestamp: new Date().toISOString()
    };
  }
}

module.exports = FailureHandler;
