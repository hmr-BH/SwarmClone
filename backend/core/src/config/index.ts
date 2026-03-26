/**
 * 配置模块
 * @module config
 */

export {
  ConfigManager,
  getConfig,
  initConfig,
  type AppConfig,
  type ServerConfig,
  type WebSocketServerConfig,
  type GrpcServerConfig,
  type LLMConfig,
  type TTSConfig,
  type ASRConfig,
  type LoggingConfig,
  type DevConfig,
} from './ConfigManager.js';
