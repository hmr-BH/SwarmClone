use anyhow::Result;
use log::info;

use crate::process::manager::ProcessManager;

pub async fn execute() -> Result<()> {
    info!("正在启动 SwarmClone 服务...");

    let mut manager = ProcessManager::new();
    manager.start_all().await?;

    info!("所有服务已启动");
    Ok(())
}
