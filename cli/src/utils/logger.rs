use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

pub fn init(verbose: bool) {
    let filter = if verbose { "debug" } else { "info" };

    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env().unwrap_or_else(|_| filter.into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();
}
