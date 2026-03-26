/**
 * 类型安全的事件发射器
 * @module events/EventEmitter
 */

import type { EventHandler } from '../types/index.js';

/**
 * 事件映射接口
 */
export interface EventMap {
  [key: string]: unknown;
}

/**
 * 类型安全的事件发射器类
 * @template T - 事件映射类型
 */
export class TypedEventEmitter<T extends EventMap> {
  private handlers: Map<keyof T, Set<EventHandler<T[keyof T]>>> = new Map();

  /**
   * 注册事件监听器
   */
  on<K extends keyof T>(event: K, handler: EventHandler<T[K]>): this {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler as EventHandler<T[keyof T]>);
    return this;
  }

  /**
   * 注册一次性事件监听器
   */
  once<K extends keyof T>(event: K, handler: EventHandler<T[K]>): this {
    const wrapper: EventHandler<T[K]> = (data) => {
      this.off(event, wrapper);
      return handler(data);
    };
    return this.on(event, wrapper);
  }

  /**
   * 移除事件监听器
   */
  off<K extends keyof T>(event: K, handler: EventHandler<T[K]>): this {
    const handlers = this.handlers.get(event);
    if (handlers) {
      handlers.delete(handler as EventHandler<T[keyof T]>);
    }
    return this;
  }

  /**
   * 触发事件
   */
  async emit<K extends keyof T>(event: K, data: T[K]): Promise<void> {
    const handlers = this.handlers.get(event);
    if (!handlers) return;

    const promises: (void | Promise<void>)[] = [];
    for (const handler of handlers) {
      try {
        promises.push(handler(data));
      } catch (error) {
        console.error(`Error in event handler for "${String(event)}":`, error);
      }
    }

    await Promise.all(promises);
  }

  /**
   * 移除所有事件监听器
   */
  removeAllListeners(event?: keyof T): this {
    if (event) {
      this.handlers.delete(event);
    } else {
      this.handlers.clear();
    }
    return this;
  }

  /**
   * 获取事件监听器数量
   */
  listenerCount(event: keyof T): number {
    return this.handlers.get(event)?.size ?? 0;
  }
}
