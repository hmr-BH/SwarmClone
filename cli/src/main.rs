use clap::{Parser, Subcommand};

mod commands;
mod config;
mod utils;

#[derive(Parser)]
#[command(name = "swarmclone")]
#[command(about = "SwarmClone CLI - 虚拟形象控制系统命令行工具", long_about = None)]
#[command(version)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
    
    #[arg(short, long, global = true)]
    verbose: bool,
}

#[derive(Subcommand)]
enum Commands {
    Deploy(commands::deploy::DeployArgs),
    Start(commands::start::StartArgs),
    Stop(commands::stop::StopArgs),
    Status(commands::status::StatusArgs),
    Config(commands::config::ConfigArgs),
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();
    
    utils::logger::init(cli.verbose);
    
    match cli.command {
        Commands::Deploy(args) => commands::deploy::execute(args).await?,
        Commands::Start(args) => commands::start::execute(args).await?,
        Commands::Stop(args) => commands::stop::execute(args).await?,
        Commands::Status(args) => commands::status::execute(args).await?,
        Commands::Config(args) => commands::config::execute(args).await?,
    }
    
    Ok(())
}
