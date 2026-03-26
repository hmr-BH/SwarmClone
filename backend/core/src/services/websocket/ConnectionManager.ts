/**
 * WebSocket连接管理器
 * @module services/websocket/ConnectionManager
 */

import WebSocket from 'ws';
import { createChildLogger } from '../../utils/logger.js';

const logger = createChildLogger('ConnectionManager');

/**
 * 客户端连接信息
 */
export interface ClientConnection {
  /** 连接ID */
  id: string;
  /** WebSocket实例 */
  socket: WebSocket;
  /** 连接时间 */
  connectedAt: number;
  /** 最后活跃时间 */
  lastActiveAt: number;
  /** 客户端元数据 */
  metadata?: Record<string, unknown>;
}

/**
 * 连接管理器配置
 */
export interface ConnectionManagerConfig {
  /** 最大连接数 */
  maxConnections?: number;
  /** 心跳间隔（毫秒） */
  heartbeatInterval?: number;
  /** 连接超时（毫秒） */
  connectionTimeout?: number;
}

/**
 * 连接管理器
 * 管理所有WebSocket客户端连接
 */
export class ConnectionManager {
  private connections: Map<string, ClientConnection> = new Map();
  private config: Required<ConnectionManagerConfig>;
  private heartbeatTimer?: ReturnType<typeof setInterval>;

  constructor(config: ConnectionManagerConfig = {}) {
    this.config = {
      maxConnections: config.maxConnections ?? 100,
      heartbeatInterval: config.heartbeatInterval ?? 30000,
      connectionTimeout: config.connectionTimeout ?? 60000,
    };
  }

  /**
   * 获取当前连接数
   */
  get connectionCount(): number {
    return this.connections.size;
  }

  /**
   * 添加连接
   */
  addConnection(socket: WebSocket): ClientConnection | null {
    if (this.connections.size >= this.config.maxConnections) {
      logger.warn(`达到最大连接数限制: ${this.config.maxConnections}`);
      socket.close(1013, '服务器繁忙');
      return null;
    }

    const id = this.generateConnectionId();
    const now = Date.now();
    const connection: ClientConnection = {
      id,
      socket,
      connectedAt: now,
      lastActiveAt: now,
    };

    this.connections.set(id, connection);
    logger.info(`客户端连接: ${id}, 当前连接数: ${this.connections.size}`);

    return connection;
  }

  /**
   * 移除连接
   */
  removeConnection(id: string): void {
    const connection = this.connections.get(id);
    if (connection) {
      this.connections.delete(id);
      logger.info(`客户端断开: ${id}, 当前连接数: ${this.connections.size}`);
    }
  }

  /**
   * 获取连接
   */
  getConnection(id: string): ClientConnection | undefined {
    return this.connections.get(id);
  }

  /**
   * 更新连接活跃时间
   */
  updateActivity(id: string): void {
    const connection = this.connections.get(id);
    if (connection) {
      connection.lastActiveAt = Date.now();
    }
  }

  /**
   * 向指定连接发送消息
   */
  send(id: string, data: string | Buffer): boolean {
    const connection = this.connections.get(id);
    if (!connection || connection.socket.readyState !== WebSocket.OPEN) {
      return false;
    }

    connection.socket.send(data);
    return true;
  }

  /**
   * 广播消息到所有连接
   */
  broadcast(data: string | Buffer, excludeIds?: string[]): void {
    const exclude = new Set(excludeIds ?? []);
    for (const [id, connection] of this.connections) {
      if (!exclude.has(id) && connection.socket.readyState === WebSocket.OPEN) {
        connection.socket.send(data);
      }
    }
  }

  /**
   * 启动心跳检测
   */
  startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      const now = Date.now();
      for (const [id, connection] of this.connections) {
        if (now - connection.lastActiveAt > this.config.connectionTimeout) {
          logger.warn(`连接超时，关闭: ${id}`);
          connection.socket.close(1001, '连接超时');
          this.removeConnection(id);
        } else if (connection.socket.readyState === WebSocket.OPEN) {
          connection.socket.ping();
        }
      }
    }, this.config.heartbeatInterval);
  }

  /**
   * 停止心跳检测
   */
  stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = undefined;
    }
  }

  /**
   * 关闭所有连接
   */
  closeAll(): void {
    for (const connection of this.connections.values()) {
      connection.socket.close(1001, '服务器关闭');
    }
    this.connections.clear();
  }

  /**
   * 生成连接ID
   */
  private generateConnectionId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
  }
}
