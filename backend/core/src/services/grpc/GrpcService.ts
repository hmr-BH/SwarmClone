/**
 * gRPC服务
 * @module services/grpc/GrpcService
 */

import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import type { PackageDefinition } from '@grpc/proto-loader';
import { BaseService } from '../index.js';
import type { GrpcConfig } from '../../types/index.js';
import { createChildLogger } from '../../utils/logger.js';
import { TypedEventEmitter } from '../../events/index.js';

const logger = createChildLogger('GrpcService');

/**
 * gRPC服务事件
 */
export interface GrpcServiceEvents {
  started: { port: number };
  stopped: void;
  error: Error;
  [key: string]: unknown;
}

/**
 * 服务实现类型
 */
export type ServiceImplementation = Record<string, grpc.UntypedHandleCall>;

/**
 * gRPC服务类
 */
export class GrpcService extends BaseService<GrpcConfig> {
  private server?: grpc.Server;
  private events = new TypedEventEmitter<GrpcServiceEvents>();
  private serviceImplementations: Map<string, ServiceImplementation> = new Map();

  constructor(config: GrpcConfig) {
    super(config);
  }

  /**
   * 获取事件发射器
   */
  get eventEmitter(): TypedEventEmitter<GrpcServiceEvents> {
    return this.events;
  }

  /**
   * 注册服务实现
   */
  registerService(name: string, implementation: ServiceImplementation): void {
    this.serviceImplementations.set(name, implementation);
    logger.info(`注册gRPC服务: ${name}`);
  }

  /**
   * 加载protobuf定义
   */
  loadProto(protoPath: string): PackageDefinition {
    const fullPath = require('path').resolve(protoPath);
    const packageDefinition = protoLoader.loadSync(fullPath, {
      keepCase: true,
      longs: String,
      enums: String,
      defaults: true,
      oneofs: true,
    });
    return packageDefinition;
  }

  /**
   * 启动gRPC服务器
   */
  protected async doStart(): Promise<void> {
    return new Promise((resolve, reject) => {
      const port = this.config.port ?? 50051;
      const host = this.config.host ?? '0.0.0.0';

      this.server = new grpc.Server();

      // 如果有配置proto路径，加载并注册服务
      if (this.config.protoPath) {
        try {
          const packageDefinition = this.loadProto(this.config.protoPath);
          const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);

          // 遍历注册所有服务
          for (const [name, implementation] of this.serviceImplementations) {
            const service = (protoDescriptor as Record<string, unknown>)[name];
            if (service && typeof service === 'object' && 'service' in service) {
              this.server!.addService(
                (service as { service: grpc.ServiceDefinition }).service,
                implementation as grpc.UntypedServiceImplementation
              );
            }
          }
        } catch (error) {
          reject(error);
          return;
        }
      }

      this.server.bindAsync(
        `${host}:${port}`,
        grpc.ServerCredentials.createInsecure(),
        (error, boundPort) => {
          if (error) {
            logger.error({ error }, 'gRPC服务器启动失败');
            reject(error);
            return;
          }

          logger.info(`gRPC服务器已启动: ${host}:${boundPort}`);
          this.events.emit('started', { port: boundPort });
          resolve();
        }
      );
    });
  }

  /**
   * 停止gRPC服务器
   */
  protected async doStop(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.server) {
        resolve();
        return;
      }

      this.server.tryShutdown((error) => {
        if (error) {
          logger.error({ error }, 'gRPC服务器关闭出错');
          reject(error);
          return;
        }

        logger.info('gRPC服务器已关闭');
        this.server = undefined;
        this.events.emit('stopped', undefined);
        resolve();
      });
    });
  }

  /**
   * 强制关闭gRPC服务器
   */
  forceShutdown(): void {
    if (this.server) {
      this.server.forceShutdown();
      this.server = undefined;
      logger.warn('gRPC服务器已强制关闭');
    }
  }
}
