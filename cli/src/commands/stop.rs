use anyhow::Result;
use log::info;

use crate::process::manager::ProcessManager;

pub async fn execute() -> Result<()> {
    info!("正在停止 SwarmClone 服务...");

    let mut manager = ProcessManager::new();
    manager.stop_all().await?;

    info!("所有服务已停止");
    Ok(())
}
