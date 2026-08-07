const winston = require('winston');
const path = require('path');
const fs = require('fs');
const config = require('../config/config');

// Ensure log directory exists
if (!fs.existsSync(config.reports.logsDir)) {
  fs.mkdirSync(config.reports.logsDir, { recursive: true });
}

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.json()
  ),
  defaultMeta: { service: 'namma-appeal-test-suite' },
  transports: [
    new winston.transports.File({
      filename: path.join(config.reports.logsDir, 'error.log'),
      level: 'error'
    }),
    new winston.transports.File({
      filename: path.join(config.reports.logsDir, 'execution.log')
    }),
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.printf(({ level, message, timestamp, suite, step }) => {
          const prefix = suite ? `[${suite}]` : '[TEST]';
          const stepInfo = step ? ` (${step})` : '';
          return `${timestamp} ${level}: ${prefix}${stepInfo} ${message}`;
        })
      )
    })
  ]
});

module.exports = logger;
