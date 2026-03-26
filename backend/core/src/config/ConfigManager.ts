/**
 * 配置管理器
 * @module config/ConfigManager
 */

import * as fs from 'fs';
import * as path from 'path';
import * as toml from '@iarna/toml';
import { createChildLogger } from '../utils/logger.js';

const logger = createChildLogger('ConfigManager');

/**
 * 服务配置
 */
export interface ServerConfig {
  host: string;
  websocket_port: number;
  grpc_port: number;
}

/**
 * WebSocket配置
 */
export interface WebSocketServerConfig {
  enabled: boolean;
  heartbeat_interval: number;
  connection_timeout: number;
  max_connections: number;
}

/**
 * gRPC配置
 */
export interface GrpcServerConfig {
  enabled: boolean;
  proto_path: string;
}

/**
 * LLM配置
 */
export interface LLMConfig {
  provider: string;
  api_key: string;
  base_url?: string;
  model: string;
  max_tokens: number;
  temperature: number;
  system_prompt: string;
}

/**
 * TTS配置
 */
export interface TTSConfig {
  provider: string;
  api_key: string;
  voice_id: string;
  speed: number;
  format: 'mp3' | 'wav' | 'ogg';
}

/**
 * ASR配置
 */
export interface ASRConfig {
  provider: string;
  api_key: string;
  language: string;
}

/**
 * 日志配置
 */
export interface LoggingConfig {
  level: string;
  pretty: boolean;
}

/**
 * 开发配置
 */
export interface DevConfig {
  enabled: boolean;
  verbose: boolean;
}

/**
 * 应用配置
 */
export interface AppConfig {
  server: ServerConfig;
  websocket: WebSocketServerConfig;
  grpc: GrpcServerConfig;
  llm: LLMConfig;
  tts: TTSConfig;
  asr: ASRConfig;
  logging: LoggingConfig;
  dev?: DevConfig;
}

/**
 * 默认配置
 */
const defaultConfig: AppConfig = {
  server: {
    host: '0.0.0.0',
    websocket_port: 8080,
    grpc_port: 50051,
  },
  websocket: {
    enabled: true,
    heartbeat_interval: 30000,
    connection_timeout: 60000,
    max_connections: 100,
  },
  grpc: {
    enabled: true,
    proto_path: './proto/vtuber.proto',
  },
  llm: {
    provider: 'openai',
    api_key: '',
    model: 'gpt-4o-mini',
    max_tokens: 2048,
    temperature: 0.7,
    system_prompt: '你是一个友善的虚拟主播助手。',
  },
  tts: {
    provider: 'openai',
    api_key: '',
    voice_id: 'alloy',
    speed: 1.0,
    format: 'mp3',
  },
  asr: {
    provider: 'openai',
    api_key: '',
    language: 'zh',
  },
  logging: {
    level: 'info',
    pretty: true,
  },
};

/**
 * 配置管理器类
 */
export class ConfigManager {
  private config: AppConfig;
  private configPath: string;

  constructor(configPath?: string) {
    this.configPath = configPath ?? this.findConfigFile();
    this.config = { ...defaultConfig };
  }

  /**
   * 查找配置文件
   */
  private findConfigFile(): string {
    const possiblePaths = [
      path.resolve(process.cwd(), 'config.toml'),
      path.resolve(process.cwd(), '..', 'config.toml'),
      path.resolve(__dirname, '../../../../config.toml'),
    ];

    for (const p of possiblePaths) {
      if (fs.existsSync(p)) {
        return p;
      }
    }

    logger.warn('未找到配置文件，使用默认配置');
    return '';
  }

  /**
   * 加载配置文件
   */
  load(): AppConfig {
    if (!this.configPath || !fs.existsSync(this.configPath)) {
      logger.warn('配置文件不存在，使用默认配置');
      return this.config;
    }

    try {
      const content = fs.readFileSync(this.configPath, 'utf-8');
      const parsed = toml.parse(content) as Partial<AppConfig>;

      // 深度合并配置
      this.config = this.mergeConfig(defaultConfig, parsed);

      logger.info(`配置已加载: ${this.configPath}`);
      return this.config;
    } catch (error) {
      logger.error({ error }, '加载配置文件失败');
      throw new Error(`加载配置文件失败: ${error}`);
    }
  }

  /**
   * 深度合并配置
   */
  private mergeConfig<T extends object>(target: T, source: Partial<T>): T {
    const result = { ...target };

    for (const key in source) {
      if (Object.prototype.hasOwnProperty.call(source, key)) {
        const sourceValue = source[key];
        const targetValue = target[key];

        if (
          sourceValue !== undefined &&
          sourceValue !== null &&
          typeof sourceValue === 'object' &&
          !Array.isArray(sourceValue) &&
          typeof targetValue === 'object' &&
          !Array.isArray(targetValue)
        ) {
          result[key] = this.mergeConfig(
            targetValue as object,
            sourceValue as Partial<object>
          ) as T[Extract<keyof T, string>];
        } else if (sourceValue !== undefined) {
          (result as Record<string, unknown>)[key] = sourceValue;
        }
      }
    }

    return result;
  }

  /**
   * 获取完整配置
   */
  getConfig(): AppConfig {
    return this.config;
  }

  /**
   * 获取指定section的配置
   */
  getSection<K extends keyof AppConfig>(section: K): AppConfig[K] {
    return this.config[section];
  }

  /**
   * 验证配置
   */
  validate(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // 验证LLM API密钥
    if (!this.config.llm.api_key || this.config.llm.api_key === 'your-api-key-here') {
      errors.push('LLM API密钥未配置');
    }

    // 验证端口范围
    if (this.config.server.websocket_port < 1 || this.config.server.websocket_port > 65535) {
      errors.push('WebSocket端口范围无效 (1-65535)');
    }

    if (this.config.server.grpc_port < 1 || this.config.server.grpc_port > 65535) {
      errors.push('gRPC端口范围无效 (1-65535)');
    }

    // 验证温度参数
    if (this.config.llm.temperature < 0 || this.config.llm.temperature > 2) {
      errors.push('LLM温度参数范围无效 (0-2)');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}

/**
 * 全局配置实例
 */
let globalConfig: ConfigManager | null = null;

/**
 * 获取全局配置实例
 */
export function getConfig(): AppConfig {
  if (!globalConfig) {
    globalConfig = new ConfigManager();
    globalConfig.load();
  }
  return globalConfig.getConfig();
}

/**
 * 初始化配置
 */
export function initConfig(configPath?: string): AppConfig {
  globalConfig = new ConfigManager(configPath);
  return globalConfig.load();
}
