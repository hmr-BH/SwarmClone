use clap::Args;
use tracing::info;

#[derive(Args)]
pub struct StopArgs {
    #[arg(short, long)]
    pub service: Option<String>,
    
    #[arg(long)]
    pub all: bool,
    
    #[arg(long)]
    pub force: bool,
}

pub async fn execute(args: StopArgs) -> anyhow::Result<()> {
    info!("停止服务...");
    
    if args.all || args.service.is_none() {
        stop_all_services(args.force).await?;
    } else if let Some(service) = &args.service {
        stop_service(service, args.force).await?;
    }
    
    Ok(())
}

async fn stop_all_services(force: bool) -> anyhow::Result<()> {
    let services = ["web", "keyboard", "vrchat", "asr", "core"];
    
    for service in services {
        stop_service(service, force).await?;
    }
    
    info!("所有服务已停止");
    Ok(())
}

async fn stop_service(name: &str, force: bool) -> anyhow::Result<()> {
    let method = if force { "强制" } else { "优雅" };
    info!("{}停止服务: {}", method, name);
    
    println!("停止服务: {} ({})", name, method);
    
    Ok(())
}
