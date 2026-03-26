/**
 * 配置系统测试
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { ConfigManager } from '../config/ConfigManager.js';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

describe('ConfigManager', () => {
  let configManager: ConfigManager;
  let tempConfigPath: string;

  beforeEach(() => {
    configManager = new ConfigManager();
  });

  it('should create instance with default config', () => {
    const config = configManager.getConfig();
    expect(config).toBeDefined();
    expect(config.server).toBeDefined();
    expect(config.llm).toBeDefined();
  });

  it('should return default config when no config file', () => {
    const config = configManager.load();
    expect(config.server.websocket_port).toBe(8080);
    expect(config.server.grpc_port).toBe(50051);
  });

  it('should get specific section', () => {
    const llmConfig = configManager.getSection('llm');
    expect(llmConfig.provider).toBe('openai');
    expect(llmConfig.model).toBe('gpt-4o-mini');
  });

  it('should validate config and return errors for missing api key', () => {
    configManager.load();
    const result = configManager.validate();
    expect(result.valid).toBe(false);
    expect(result.errors).toContain('LLM API密钥未配置');
  });

  it('should load config from file', async () => {
    // 创建临时配置文件
    tempConfigPath = path.join(os.tmpdir(), `config-${Date.now()}.toml`);
    const configContent = `
[server]
host = "127.0.0.1"
websocket_port = 9000
grpc_port = 60000

[llm]
api_key = "test-key-12345"
model = "gpt-4"
`;

    fs.writeFileSync(tempConfigPath, configContent);

    const manager = new ConfigManager(tempConfigPath);
    const config = manager.load();

    expect(config.server.host).toBe('127.0.0.1');
    expect(config.server.websocket_port).toBe(9000);
    expect(config.server.grpc_port).toBe(60000);
    expect(config.llm.api_key).toBe('test-key-12345');
    expect(config.llm.model).toBe('gpt-4');

    // 清理
    fs.unlinkSync(tempConfigPath);
  });

  it('should validate port range', async () => {
    tempConfigPath = path.join(os.tmpdir(), `config-invalid-${Date.now()}.toml`);
    const configContent = `
[server]
websocket_port = 99999
grpc_port = 0
`;

    fs.writeFileSync(tempConfigPath, configContent);

    const manager = new ConfigManager(tempConfigPath);
    manager.load();
    const result = manager.validate();

    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.includes('WebSocket端口'))).toBe(true);
    expect(result.errors.some(e => e.includes('gRPC端口'))).toBe(true);

    fs.unlinkSync(tempConfigPath);
  });

  it('should validate temperature range', async () => {
    tempConfigPath = path.join(os.tmpdir(), `config-temp-${Date.now()}.toml`);
    const configContent = `
[llm]
api_key = "test-key"
temperature = 3.0
`;

    fs.writeFileSync(tempConfigPath, configContent);

    const manager = new ConfigManager(tempConfigPath);
    manager.load();
    const result = manager.validate();

    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.includes('温度参数'))).toBe(true);

    fs.unlinkSync(tempConfigPath);
  });

  it('should merge partial config with defaults', async () => {
    tempConfigPath = path.join(os.tmpdir(), `config-partial-${Date.now()}.toml`);
    const configContent = `
[server]
websocket_port = 9999

[llm]
api_key = "my-key"
`;

    fs.writeFileSync(tempConfigPath, configContent);

    const manager = new ConfigManager(tempConfigPath);
    const config = manager.load();

    // 覆盖的值
    expect(config.server.websocket_port).toBe(9999);
    expect(config.llm.api_key).toBe('my-key');

    // 未覆盖的值应使用默认值
    expect(config.server.grpc_port).toBe(50051);
    expect(config.llm.model).toBe('gpt-4o-mini');
    expect(config.websocket.enabled).toBe(true);

    fs.unlinkSync(tempConfigPath);
  });
});
