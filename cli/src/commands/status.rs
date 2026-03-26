use clap::Args;
use tracing::info;

#[derive(Args)]
pub struct StatusArgs {
    #[arg(short, long)]
    pub service: Option<String>,
    
    #[arg(short, long)]
    pub json: bool,
}

pub async fn execute(args: StatusArgs) -> anyhow::Result<()> {
    info!("查询系统状态...");
    
    let status = get_system_status().await?;
    
    if args.json {
        println!("{}", serde_json::to_string_pretty(&status)?);
    } else {
        print_status(&status);
    }
    
    Ok(())
}

#[derive(serde::Serialize)]
struct ServiceStatus {
    name: String,
    status: String,
    uptime: Option<f64>,
}

#[derive(serde::Serialize)]
struct SystemStatus {
    version: String,
    services: Vec<ServiceStatus>,
}

async fn get_system_status() -> anyhow::Result<SystemStatus> {
    Ok(SystemStatus {
        version: env!("CARGO_PKG_VERSION").to_string(),
        services: vec![
            ServiceStatus {
                name: "core".to_string(),
                status: "running".to_string(),
                uptime: Some(3600.0),
            },
            ServiceStatus {
                name: "asr".to_string(),
                status: "running".to_string(),
                uptime: Some(3600.0),
            },
            ServiceStatus {
                name: "vrchat".to_string(),
                status: "stopped".to_string(),
                uptime: None,
            },
            ServiceStatus {
                name: "keyboard".to_string(),
                status: "running".to_string(),
                uptime: Some(3600.0),
            },
            ServiceStatus {
                name: "web".to_string(),
                status: "running".to_string(),
                uptime: Some(3600.0),
            },
        ],
    })
}

fn print_status(status: &SystemStatus) {
    println!("SwarmClone v{}", status.version);
    println!();
    println!("{:<15} {:<12} {}", "服务", "状态", "运行时间");
    println!("{}", "-".repeat(40));
    
    for service in &status.services {
        let uptime = service
            .uptime
            .map(|t| format!("{:.0}s", t))
            .unwrap_or_else(|| "-".to_string());
        
        let status_icon = match service.status.as_str() {
            "running" => "🟢",
            "stopped" => "🔴",
            "error" => "⚠️",
            _ => "⚪",
        };
        
        println!("{:<15} {} {:<10} {}", service.name, status_icon, service.status, uptime);
    }
}
