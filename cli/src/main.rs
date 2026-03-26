mod commands;
mod process;

use clap::{Parser, Subcommand};
use commands::{init, start, status, stop};

#[derive(Parser)]
#[command(name = "swarmclone")]
#[command(about = "SwarmClone 多语言项目部署管理工具", long_about = None)]
#[command(version)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    #[command(about = "初始化开发环境")]
    Init,
    #[command(about = "启动所有服务")]
    Start,
    #[command(about = "停止所有服务")]
    Stop,
    #[command(about = "查看服务状态")]
    Status,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    env_logger::init();

    let cli = Cli::parse();

    match cli.command {
        Commands::Init => init::execute().await?,
        Commands::Start => start::execute().await?,
        Commands::Stop => stop::execute().await?,
        Commands::Status => status::execute().await?,
    }

    Ok(())
}
