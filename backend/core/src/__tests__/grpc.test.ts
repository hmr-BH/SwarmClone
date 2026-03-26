/**
 * gRPC服务测试
 */

import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { GrpcService } from '../services/grpc/GrpcService.js';
import type { GrpcConfig } from '../types/index.js';
import { ServiceStatus } from '../types/index.js';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

describe('GrpcService', () => {
  let service: GrpcService;
  const config: GrpcConfig = {
    name: 'test-grpc',
    enabled: true,
    port: 50051,
    host: '127.0.0.1',
    protoPath: path.resolve(__dirname, '../../proto/vtuber.proto'),
  };

  beforeAll(async () => {
    service = new GrpcService(config);
  });

  afterAll(async () => {
    if (service.getStatus() === ServiceStatus.RUNNING) {
      await service.stop();
    }
  });

  it('should create service with correct config', () => {
    expect(service.name).toBe('test-grpc');
    expect(service.getStatus()).toBe(ServiceStatus.STOPPED);
  });

  it('should start service successfully', async () => {
    await service.start();
    expect(service.getStatus()).toBe(ServiceStatus.RUNNING);
  });

  it('should emit started event', async () => {
    const newService = new GrpcService({
      ...config,
      port: 50052,
    });

    const startedPromise = new Promise<number>((resolve) => {
      newService.eventEmitter.once('started', ({ port }) => resolve(port));
    });

    await newService.start();
    const port = await startedPromise;
    expect(port).toBe(50052);

    await newService.stop();
  });

  it('should stop service successfully', async () => {
    await service.stop();
    expect(service.getStatus()).toBe(ServiceStatus.STOPPED);
  });

  it('should load proto file correctly', () => {
    const newService = new GrpcService(config);
    const packageDef = newService.loadProto(config.protoPath!);
    expect(packageDef).toBeDefined();
    expect(Object.keys(packageDef).length).toBeGreaterThan(0);
  });

  it('should handle multiple start/stop cycles', async () => {
    const newService = new GrpcService({
      ...config,
      port: 50053,
    });

    for (let i = 0; i < 3; i++) {
      await newService.start();
      expect(newService.getStatus()).toBe(ServiceStatus.RUNNING);
      await newService.stop();
      expect(newService.getStatus()).toBe(ServiceStatus.STOPPED);
    }
  });
});
