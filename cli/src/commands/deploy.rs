use clap::Args;
use tracing::info;

#[derive(Args)]
pub struct DeployArgs {
    #[arg(short, long, default_value = "development")]
    pub mode: String,
    
    #[arg(short, long)]
    pub config_path: Option<String>,
    
    #[arg(long)]
    pub skip_deps: bool,
}

pub async fn execute(args: DeployArgs) -> anyhow::Result<()> {
    info!("开始部署 SwarmClone...");
    info!("部署模式: {}", args.mode);
    
    if !args.skip_deps {
        check_dependencies().await?;
    }
    
    generate_config(&args.mode, args.config_path.as_deref()).await?;
    
    info!("部署完成!");
    Ok(())
}

async fn check_dependencies() -> anyhow::Result<()> {
    use indicatif::ProgressBar;
    use which::which;
    
    let pb = ProgressBar::new_spinner();
    pb.set_message("检查依赖...");
    
    let dependencies = ["python", "pip", "node", "cargo"];
    let mut missing = Vec::new();
    
    for dep in dependencies {
        if which(dep).is_err() {
            missing.push(dep);
        }
    }
    
    pb.finish_and_clear();
    
    if !missing.is_empty() {
        println!("缺失依赖: {}", missing.join(", "));
        println!("请先安装缺失的依赖项");
    } else {
        println!("所有依赖已安装");
    }
    
    Ok(())
}

async fn generate_config(mode: &str, config_path: Option<&str>) -> anyhow::Result<()> {
    use std::path::Path;
    
    let config_dir = config_path.unwrap_or("config");
    let config_path = Path::new(config_dir);
    
    if !config_path.exists() {
        std::fs::create_dir_all(config_path)?;
        info!("创建配置目录: {}", config_dir);
    }
    
    let config_file = config_path.join("config.yaml");
    if !config_file.exists() {
        let default_config = format!(
            r#"system:
  mode: {}
  log_level: INFO

services:
  asr:
    enabled: true
    engine: whisper
    model: base
  vrchat:
    enabled: true
    osc_port: 9000
  keyboard:
    enabled: true

messaging:
  redis:
    host: localhost
    port: 6379
"#,
            mode
        );
        std::fs::write(&config_file, default_config)?;
        info!("生成默认配置文件: {:?}", config_file);
    }
    
    Ok(())
}
