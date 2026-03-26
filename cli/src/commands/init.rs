use anyhow::Result;
use log::info;
use which::which;

pub async fn execute() -> Result<()> {
    info!("正在初始化 SwarmClone 开发环境...");

    check_python()?;
    check_node()?;
    check_rust()?;

    info!("环境初始化完成！");
    info!("请运行 'swarmclone start' 启动服务");

    Ok(())
}

fn check_python() -> Result<()> {
    match which("python") {
        Ok(_) => {
            info!("✓ Python 已安装");
            Ok(())
        }
        Err(_) => {
            info!("✗ Python 未安装，请安装 Python 3.12+");
            Ok(())
        }
    }
}

fn check_node() -> Result<()> {
    match which("node") {
        Ok(_) => {
            info!("✓ Node.js 已安装");
            Ok(())
        }
        Err(_) => {
            info!("✗ Node.js 未安装，请安装 Node.js 18+");
            Ok(())
        }
    }
}

fn check_rust() -> Result<()> {
    match which("cargo") {
        Ok(_) => {
            info!("✓ Rust/Cargo 已安装");
            Ok(())
        }
        Err(_) => {
            info!("✗ Rust 未安装，请安装 Rust");
            Ok(())
        }
    }
}
