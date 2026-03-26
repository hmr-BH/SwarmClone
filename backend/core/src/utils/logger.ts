/**
 * 日志工具模块
 * @module utils/logger
 */

import pino from 'pino';

/**
 * 日志级别
 */
export type LogLevel = 'trace' | 'debug' | 'info' | 'warn' | 'error' | 'fatal';

/**
 * 日志配置
 */
export interface LoggerConfig {
  /** 日志级别 */
  level?: LogLevel;
  /** 服务名称 */
  service?: string;
  /** 是否启用美化输出 */
  pretty?: boolean;
}

/**
 * 创建日志实例
 */
export function createLogger(config: LoggerConfig = {}): pino.Logger {
  const { level = 'info', service = 'vtuber-core', pretty = true } = config;

  const baseConfig: pino.LoggerOptions = {
    level,
    base: { service },
    timestamp: pino.stdTimeFunctions.isoTime,
  };

  if (pretty) {
    return pino({
      ...baseConfig,
      transport: {
        target: 'pino-pretty',
        options: {
          colorize: true,
          translateTime: 'SYS:standard',
          ignore: 'pid,hostname',
        },
      },
    });
  }

  return pino(baseConfig);
}

/**
 * 默认日志实例
 */
export const logger = createLogger();

/**
 * 创建子日志实例
 */
export function createChildLogger(name: string): pino.Logger {
  return logger.child({ module: name });
}
