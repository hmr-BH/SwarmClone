/**
 * 核心类型定义
 * @module types
 */

/**
 * 服务状态枚举
 */
export enum ServiceStatus {
  STOPPED = 'stopped',
  STARTING = 'starting',
  RUNNING = 'running',
  STOPPING = 'stopping',
  ERROR = 'error',
}

/**
 * 基础服务配置接口
 */
export interface BaseServiceConfig {
  /** 服务名称 */
  name: string;
  /** 是否启用 */
  enabled: boolean;
  /** 服务端口 */
  port?: number;
  /** 服务主机 */
  host?: string;
}

/**
 * WebSocket配置接口
 */
export interface WebSocketConfig extends BaseServiceConfig {
  /** 心跳间隔（毫秒） */
  heartbeatInterval?: number;
  /** 最大连接数 */
  maxConnections?: number;
}

/**
 * gRPC配置接口
 */
export interface GrpcConfig extends BaseServiceConfig {
  /** protobuf文件路径 */
  protoPath?: string;
}

/**
 * AI服务配置接口
 */
export interface AIServiceConfig extends BaseServiceConfig {
  /** API密钥 */
  apiKey?: string;
  /** API基础URL */
  baseUrl?: string;
  /** 模型名称 */
  model?: string;
}

/**
 * LLM服务配置
 */
export interface LLMConfig extends AIServiceConfig {
  /** 最大令牌数 */
  maxTokens?: number;
  /** 温度参数 */
  temperature?: number;
  /** 系统提示词 */
  systemPrompt?: string;
}

/**
 * TTS服务配置
 */
export interface TTSConfig extends AIServiceConfig {
  /** 语音ID */
  voiceId?: string;
  /** 语速 */
  speed?: number;
  /** 输出格式 */
  format?: 'mp3' | 'wav' | 'ogg';
}

/**
 * ASR服务配置
 */
export interface ASRConfig extends AIServiceConfig {
  /** 语言代码 */
  language?: string;
  /** 采样率 */
  sampleRate?: number;
}

/**
 * 消息类型枚举
 */
export enum MessageType {
  TEXT = 'text',
  AUDIO = 'audio',
  VIDEO = 'video',
  CONTROL = 'control',
  SYSTEM = 'system',
}

/**
 * 基础消息接口
 */
export interface BaseMessage {
  /** 消息ID */
  id: string;
  /** 消息类型 */
  type: MessageType;
  /** 时间戳 */
  timestamp: number;
  /** 发送者ID */
  senderId?: string;
  /** 元数据 */
  metadata?: Record<string, unknown>;
}

/**
 * 文本消息接口
 */
export interface TextMessage extends BaseMessage {
  type: MessageType.TEXT;
  /** 文本内容 */
  content: string;
}

/**
 * 音频消息接口
 */
export interface AudioMessage extends BaseMessage {
  type: MessageType.AUDIO;
  /** 音频数据 */
  data: Buffer;
  /** 音频格式 */
  format: string;
  /** 时长（毫秒） */
  duration?: number;
}

/**
 * 控制消息接口
 */
export interface ControlMessage extends BaseMessage {
  type: MessageType.CONTROL;
  /** 控制命令 */
  command: string;
  /** 命令参数 */
  params?: Record<string, unknown>;
}

/**
 * 消息联合类型
 */
export type Message = TextMessage | AudioMessage | ControlMessage;

/**
 * 事件处理器类型
 */
export type EventHandler<T = unknown> = (data: T) => void | Promise<void>;

/**
 * 服务健康状态
 */
export interface HealthStatus {
  /** 服务名称 */
  service: string;
  /** 状态 */
  status: ServiceStatus;
  /** 最后检查时间 */
  lastCheck: number;
  /** 错误信息 */
  error?: string;
  /** 额外信息 */
  details?: Record<string, unknown>;
}
