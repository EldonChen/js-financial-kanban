use mongodb::{Client, Database};
use std::env;

pub async fn connect_to_mongo() -> Result<Database, mongodb::error::Error> {
    let mongodb_url = env::var("MONGODB_URL").unwrap_or_else(|_| "mongodb://localhost:27017".to_string());
    let database_name = env::var("DATABASE_NAME").unwrap_or_else(|_| "financial_kanban".to_string());

    let client = Client::with_uri_str(&mongodb_url).await?;
    let db = client.database(&database_name);

    println!("✅ 已连接到 MongoDB: {}", database_name);
    Ok(db)
}
