use anyhow::Result;
use log::info;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use sysinfo::System;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServiceInfo {
    pub name: String,
    pub status: ServiceStatus,
    pub pid: Option<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ServiceStatus {
    Running,
    Stopped,
    Unknown,
}

pub struct ProcessManager {
    services: HashMap<String, ServiceInfo>,
}

impl ProcessManager {
    pub fn new() -> Self {
        let mut services = HashMap::new();

        services.insert(
            "core".to_string(),
            ServiceInfo {
                name: "Core (Python)".to_string(),
                status: ServiceStatus::Unknown,
                pid: None,
            },
        );

        services.insert(
            "panel".to_string(),
            ServiceInfo {
                name: "Panel (Vue.js)".to_string(),
                status: ServiceStatus::Unknown,
                pid: None,
            },
        );

        services.insert(
            "frontend".to_string(),
            ServiceInfo {
                name: "Frontend (Godot)".to_string(),
                status: ServiceStatus::Unknown,
                pid: None,
            },
        );

        Self { services }
    }

    pub async fn start_all(&mut self) -> Result<()> {
        for (key, service) in &mut self.services {
            info!("启动服务: {}", service.name);
            service.status = ServiceStatus::Running;
        }
        Ok(())
    }

    pub async fn stop_all(&mut self) -> Result<()> {
        for (key, service) in &mut self.services {
            info!("停止服务: {}", service.name);
            service.status = ServiceStatus::Stopped;
        }
        Ok(())
    }

    pub async fn show_status(&self) -> Result<()> {
        let mut sys = System::new_all();
        sys.refresh_all();

        println!("\n{:<20} {:<15}", "服务名称", "状态");
        println!("{}", "-".repeat(35));

        for (_, service) in &self.services {
            let status_str = match service.status {
                ServiceStatus::Running => "🟢 运行中",
                ServiceStatus::Stopped => "🔴 已停止",
                ServiceStatus::Unknown => "⚪ 未知",
            };
            println!("{:<20} {:<15}", service.name, status_str);
        }

        println!();
        Ok(())
    }
}

impl Default for ProcessManager {
    fn default() -> Self {
        Self::new()
    }
}
