/**
 * WebSocket服务
 * @module services/websocket/WebSocketService
 */

import WebSocket, { WebSocketServer } from 'ws';
import { BaseService } from '../index.js';
import { TypedEventEmitter } from '../../events/index.js';
import type { WebSocketConfig, Message, MessageType } from '../../types/index.js';
import { ConnectionManager } from './ConnectionManager.js';
import { createChildLogger } from '../../utils/logger.js';

const logger = createChildLogger('WebSocketService');

/**
 * WebSocket服务事件
 */
export interface WebSocketServiceEvents {
  connection: { clientId: string; socket: WebSocket };
  disconnection: { clientId: string; reason: string };
  message: { clientId: string; message: Message };
  error: { clientId?: string; error: Error };
  [key: string]: unknown;
}

/**
 * WebSocket服务类
 */
export class WebSocketService extends BaseService<WebSocketConfig> {
  private server?: WebSocketServer;
  private connectionManager: ConnectionManager;
  private events = new TypedEventEmitter<WebSocketServiceEvents>();

  constructor(config: WebSocketConfig) {
    super(config);
    this.connectionManager = new ConnectionManager({
      maxConnections: config.maxConnections,
      heartbeatInterval: config.heartbeatInterval,
    });
  }

  /**
   * 获取事件发射器
   */
  get eventEmitter(): TypedEventEmitter<WebSocketServiceEvents> {
    return this.events;
  }

  /**
   * 获取当前连接数
   */
  get connectionCount(): number {
    return this.connectionManager.connectionCount;
  }

  /**
   * 启动WebSocket服务器
   */
  protected async doStart(): Promise<void> {
    return new Promise((resolve, reject) => {
      const port = this.config.port ?? 8080;
      const host = this.config.host ?? '0.0.0.0';

      this.server = new WebSocketServer({ port, host });

      this.server.on('listening', () => {
        logger.info(`WebSocket服务器已启动: ws://${host}:${port}`);
        this.connectionManager.startHeartbeat();
        resolve();
      });

      this.server.on('error', (error) => {
        logger.error({ error }, 'WebSocket服务器错误');
        reject(error);
      });

      this.server.on('connection', (socket, _request) => {
        this.handleConnection(socket);
      });
    });
  }

  /**
   * 停止WebSocket服务器
   */
  protected async doStop(): Promise<void> {
    return new Promise((resolve) => {
      if (!this.server) {
        resolve();
        return;
      }

      this.connectionManager.stopHeartbeat();
      this.connectionManager.closeAll();

      this.server.close(() => {
        logger.info('WebSocket服务器已关闭');
        this.server = undefined;
        resolve();
      });
    });
  }

  /**
   * 处理新连接
   */
  private handleConnection(socket: WebSocket): void {
    const connection = this.connectionManager.addConnection(socket);
    if (!connection) return;

    const clientId = connection.id;

    // 设置消息处理器
    socket.on('message', (data) => {
      this.handleMessage(clientId, data);
    });

    socket.on('close', (code, reason) => {
      this.connectionManager.removeConnection(clientId);
      this.events.emit('disconnection', {
        clientId,
        reason: reason.toString() || `代码: ${code}`,
      });
    });

    socket.on('error', (error) => {
      logger.error({ clientId, error }, '客户端错误');
      this.events.emit('error', { clientId, error });
    });

    socket.on('pong', () => {
      this.connectionManager.updateActivity(clientId);
    });

    // 触发连接事件
    this.events.emit('connection', { clientId, socket });
  }

  /**
   * 处理接收到的消息
   */
  private handleMessage(clientId: string, data: WebSocket.RawData): void {
    this.connectionManager.updateActivity(clientId);

    try {
      const rawMessage = JSON.parse(data.toString());
      const message = this.parseMessage(rawMessage);

      if (message) {
        this.events.emit('message', { clientId, message });
      }
    } catch (error) {
      const errMsg = error instanceof Error ? error.message : String(error);
      logger.warn({ clientId, error: errMsg }, '解析消息失败');
      this.send(clientId, {
        type: 'error',
        error: '消息格式错误',
        originalData: data.toString(),
      });
    }
  }

  /**
   * 解析消息
   */
  private parseMessage(raw: unknown): Message | null {
    if (typeof raw !== 'object' || raw === null) return null;

    const obj = raw as Record<string, unknown>;

    if (typeof obj['id'] !== 'string' || typeof obj['type'] !== 'string') {
      return null;
    }

    return {
      id: obj['id'] as string,
      type: obj['type'] as MessageType,
      timestamp: typeof obj['timestamp'] === 'number' ? obj['timestamp'] : Date.now(),
      senderId: obj['senderId'] as string | undefined,
      metadata: obj['metadata'] as Record<string, unknown> | undefined,
      ...obj,
    } as Message;
  }

  /**
   * 向指定客户端发送消息
   */
  send(clientId: string, data: object): boolean {
    const json = JSON.stringify(data);
    return this.connectionManager.send(clientId, json);
  }

  /**
   * 广播消息到所有客户端
   */
  broadcast(data: object, excludeClientIds?: string[]): void {
    const json = JSON.stringify(data);
    this.connectionManager.broadcast(json, excludeClientIds);
  }

  /**
   * 获取所有客户端ID
   */
  getClientIds(): string[] {
    return Array.from(this.connectionManager['connections'].keys());
  }
}
