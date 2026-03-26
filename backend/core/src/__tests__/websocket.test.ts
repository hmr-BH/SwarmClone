/**
 * WebSocket服务测试
 */

import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import WebSocket from 'ws';
import { WebSocketService } from '../services/websocket/WebSocketService.js';
import type { WebSocketConfig } from '../types/index.js';
import { ServiceStatus } from '../types/index.js';

describe('WebSocketService', () => {
  let service: WebSocketService;
  const config: WebSocketConfig = {
    name: 'test-ws',
    enabled: true,
    port: 18080,
    host: '127.0.0.1',
  };

  beforeAll(async () => {
    service = new WebSocketService(config);
    await service.start();
  });

  afterAll(async () => {
    await service.stop();
  });

  it('should start and be in running status', () => {
    expect(service.getStatus()).toBe(ServiceStatus.RUNNING);
  });

  it('should accept WebSocket connections', async () => {
    const ws = new WebSocket(`ws://${config.host}:${config.port}`);

    await new Promise<void>((resolve, reject) => {
      ws.on('open', () => {
        resolve();
      });
      ws.on('error', reject);
    });

    expect(service.connectionCount).toBe(1);
    ws.close();
  });

  it('should emit connection event', async () => {
    const connectionPromise = new Promise<string>((resolve) => {
      service.eventEmitter.once('connection', ({ clientId }) => {
        resolve(clientId);
      });
    });

    const ws = new WebSocket(`ws://${config.host}:${config.port}`);
    await new Promise<void>((resolve) => ws.on('open', resolve));

    const clientId = await connectionPromise;
    expect(clientId).toBeDefined();
    ws.close();
  });

  it('should receive and parse messages', async () => {
    const messagePromise = new Promise<unknown>((resolve) => {
      service.eventEmitter.once('message', ({ message }) => {
        resolve(message);
      });
    });

    const ws = new WebSocket(`ws://${config.host}:${config.port}`);
    await new Promise<void>((resolve) => ws.on('open', resolve));

    const testMessage = {
      id: 'test-msg-1',
      type: 'text',
      content: 'Hello World',
    };

    ws.send(JSON.stringify(testMessage));

    const received = await messagePromise as Record<string, unknown>;
    expect(received['id']).toBe(testMessage.id);
    expect(received['type']).toBe(testMessage.type);

    ws.close();
  });

  it('should send messages to clients', async () => {
    // 先设置连接事件监听
    const connectionPromise = new Promise<string>((resolve) => {
      service.eventEmitter.once('connection', ({ clientId }) => resolve(clientId));
    });

    const ws = new WebSocket(`ws://${config.host}:${config.port}`);

    // 等待连接打开和获取clientId
    await new Promise<void>((resolve) => ws.on('open', resolve));
    const clientId = await connectionPromise;

    // 设置消息接收
    const messagePromise = new Promise<string>((resolve) => {
      ws.once('message', (data) => {
        resolve(data.toString());
      });
    });

    // 发送消息
    const testResponse = { type: 'test', data: 'response' };
    service.send(clientId, testResponse);

    const received = await messagePromise;
    expect(JSON.parse(received)).toEqual(testResponse);

    ws.close();
  });
});
