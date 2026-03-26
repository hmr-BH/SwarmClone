/**
 * AI虚拟主播系统核心模块
 * @module @vtuber/core
 */

// 版本号
export const VERSION = '0.1.0';

// 导出类型
export * from './types/index.js';

// 导出事件系统
export * from './events/index.js';

// 导出服务基类
export * from './services/index.js';

// 导出工具
export { createLogger, createChildLogger, logger, type LoggerConfig, type LogLevel } from './utils/logger.js';
