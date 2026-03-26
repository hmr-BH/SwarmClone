use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Debug, Serialize, Deserialize)]
pub struct AppConfig {
    pub system: SystemConfig,
    pub services: ServicesConfig,
    pub messaging: MessagingConfig,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SystemConfig {
    pub mode: String,
    pub log_level: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ServicesConfig {
    pub asr: AsrConfig,
    pub vrchat: VrchatConfig,
    pub keyboard: KeyboardConfig,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct AsrConfig {
    pub enabled: bool,
    pub engine: String,
    pub model: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VrchatConfig {
    pub enabled: bool,
    pub osc_port: u16,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct KeyboardConfig {
    pub enabled: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MessagingConfig {
    pub redis: RedisConfig,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RedisConfig {
    pub host: String,
    pub port: u16,
}

impl AppConfig {
    pub fn load(path: &Path) -> anyhow::Result<Self> {
        let content = std::fs::read_to_string(path)?;
        let config: AppConfig = serde_yaml::from_str(&content)?;
        Ok(config)
    }

    pub fn save(&self, path: &Path) -> anyhow::Result<()> {
        let content = serde_yaml::to_string(self)?;
        std::fs::write(path, content)?;
        Ok(())
    }
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            system: SystemConfig {
                mode: "development".to_string(),
                log_level: "INFO".to_string(),
            },
            services: ServicesConfig {
                asr: AsrConfig {
                    enabled: true,
                    engine: "whisper".to_string(),
                    model: "base".to_string(),
                },
                vrchat: VrchatConfig {
                    enabled: true,
                    osc_port: 9000,
                },
                keyboard: KeyboardConfig { enabled: true },
            },
            messaging: MessagingConfig {
                redis: RedisConfig {
                    host: "localhost".to_string(),
                    port: 6379,
                },
            },
        }
    }
}
