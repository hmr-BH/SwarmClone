use anyhow::Result;
use log::info;

use crate::process::manager::ProcessManager;

pub async fn execute() -> Result<()> {
    info!("SwarmClone 服务状态：");

    let manager = ProcessManager::new();
    manager.show_status().await?;

    Ok(())
}
