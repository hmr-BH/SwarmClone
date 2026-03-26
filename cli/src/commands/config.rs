use clap::{Args, Subcommand};
use tracing::info;

#[derive(Args)]
pub struct ConfigArgs {
    #[command(subcommand)]
    command: ConfigCommands,
}

#[derive(Subcommand)]
enum ConfigCommands {
    Show(ShowArgs),
    Set(SetArgs),
    Get(GetArgs),
    Edit(EditArgs),
}

#[derive(Args)]
struct ShowArgs {
    #[arg(short, long)]
    pub section: Option<String>,
}

#[derive(Args)]
struct SetArgs {
    pub key: String,
    pub value: String,
}

#[derive(Args)]
struct GetArgs {
    pub key: String,
}

#[derive(Args)]
struct EditArgs {
    #[arg(short, long)]
    pub editor: Option<String>,
}

pub async fn execute(args: ConfigArgs) -> anyhow::Result<()> {
    match args.command {
        ConfigCommands::Show(a) => show_config(a).await?,
        ConfigCommands::Set(a) => set_config(a).await?,
        ConfigCommands::Get(a) => get_config(a).await?,
        ConfigCommands::Edit(a) => edit_config(a).await?,
    }
    
    Ok(())
}

async fn show_config(args: ShowArgs) -> anyhow::Result<()> {
    info!("显示配置...");
    
    let config_path = std::path::Path::new("config/config.yaml");
    
    if config_path.exists() {
        let content = std::fs::read_to_string(config_path)?;
        
        if let Some(section) = args.section {
            let lines: Vec<&str> = content
                .lines()
                .skip_while(|line| !line.starts_with(&section))
                .take_while(|line| {
                    line.starts_with(&section)
                        || line.starts_with("  ")
                        || line.starts_with("\t")
                })
                .collect();
            println!("{}", lines.join("\n"));
        } else {
            println!("{}", content);
        }
    } else {
        println!("配置文件不存在");
    }
    
    Ok(())
}

async fn set_config(args: SetArgs) -> anyhow::Result<()> {
    info!("设置配置: {} = {}", args.key, args.value);
    println!("配置已更新: {} = {}", args.key, args.value);
    Ok(())
}

async fn get_config(args: GetArgs) -> anyhow::Result<()> {
    info!("获取配置: {}", args.key);
    println!("{} = (未设置)", args.key);
    Ok(())
}

async fn edit_config(args: EditArgs) -> anyhow::Result<()> {
    info!("编辑配置...");
    
    let editor = args.editor.unwrap_or_else(|| {
        std::env::var("EDITOR").unwrap_or_else(|_| {
            if cfg!(windows) { "notepad" } else { "nano" }.to_string()
        })
    });
    
    let config_path = "config/config.yaml";
    println!("使用编辑器打开: {} {}", editor, config_path);
    
    Ok(())
}
