/**
 * 服务模块
 * @module services
 */

import { ServiceStatus, type BaseServiceConfig, type HealthStatus } from '../types/index.js';
import { TypedEventEmitter } from '../events/index.js';
import { createChildLogger } from '../utils/logger.js';

/**
 * 服务事件映射
 */
export interface ServiceEvents {
  statusChange: { from: ServiceStatus; to: ServiceStatus };
  error: Error;
  start: void;
  stop: void;
  [key: string]: unknown;
}

/**
 * 服务基类
 * @template C - 配置类型
 * @template E - 事件类型
 */
export abstract class BaseService<C extends BaseServiceConfig = BaseServiceConfig> extends TypedEventEmitter<ServiceEvents> {
  protected config: C;
  protected status: ServiceStatus = ServiceStatus.STOPPED;
  protected logger = createChildLogger(this.constructor.name);

  constructor(config: C) {
    super();
    this.config = config;
  }

  /**
   * 获取服务名称
   */
  get name(): string {
    return this.config.name;
  }

  /**
   * 获取当前状态
   */
  getStatus(): ServiceStatus {
    return this.status;
  }

  /**
   * 设置状态并触发事件
   */
  protected async setStatus(newStatus: ServiceStatus): Promise<void> {
    const oldStatus = this.status;
    if (oldStatus === newStatus) return;

    this.status = newStatus;
    await this.emit('statusChange', { from: oldStatus, to: newStatus });
  }

  /**
   * 启动服务
   */
  async start(): Promise<void> {
    if (this.status !== ServiceStatus.STOPPED) {
      throw new Error(`服务 ${this.name} 已经在运行或正在启动`);
    }

    try {
      await this.setStatus(ServiceStatus.STARTING);
      await this.doStart();
      await this.setStatus(ServiceStatus.RUNNING);
      await this.emit('start', undefined);
      this.logger.info(`服务 ${this.name} 已启动`);
    } catch (error) {
      await this.setStatus(ServiceStatus.ERROR);
      const err = error instanceof Error ? error : new Error(String(error));
      await this.emit('error', err);
      throw err;
    }
  }

  /**
   * 停止服务
   */
  async stop(): Promise<void> {
    if (this.status === ServiceStatus.STOPPED) {
      return;
    }

    try {
      await this.setStatus(ServiceStatus.STOPPING);
      await this.doStop();
      await this.setStatus(ServiceStatus.STOPPED);
      await this.emit('stop', undefined);
      this.logger.info(`服务 ${this.name} 已停止`);
    } catch (error) {
      await this.setStatus(ServiceStatus.ERROR);
      const err = error instanceof Error ? error : new Error(String(error));
      await this.emit('error', err);
      throw err;
    }
  }

  /**
   * 获取健康状态
   */
  async getHealth(): Promise<HealthStatus> {
    return {
      service: this.name,
      status: this.status,
      lastCheck: Date.now(),
    };
  }

  /**
   * 子类实现具体启动逻辑
   */
  protected abstract doStart(): Promise<void>;

  /**
   * 子类实现具体停止逻辑
   */
  protected abstract doStop(): Promise<void>;
}
