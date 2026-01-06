mod database;
mod handlers;
mod models;

use axum::{
    http::StatusCode,
    response::Json,
    routing::{delete, get, post, put},
    Router,
};
use dotenv::dotenv;
use mongodb::Database;
use std::env;
use tower_http::cors::CorsLayer;

use crate::database::connect_to_mongo;
use crate::handlers::items::{
    create_item, delete_item, get_item, get_items, update_item,
};
use crate::models::item::ApiResponse;

#[tokio::main]
async fn main() {
    // 加载环境变量
    dotenv().ok();

    // 连接 MongoDB
    let db = connect_to_mongo()
        .await
        .expect("Failed to connect to MongoDB");

    // 构建应用路由
    let app = Router::new()
        .route("/", get(root))
        .route("/health", get(health))
        .route("/api/v1/items", get(get_items).post(create_item))
        .route(
            "/api/v1/items/:id",
            get(get_item).put(update_item).delete(delete_item),
        )
        .layer(CorsLayer::permissive())
        .with_state(db);

    // 启动服务器
    let port = env::var("PORT").unwrap_or_else(|_| "8080".to_string());
    let addr = format!("0.0.0.0:{}", port);
    let listener = tokio::net::TcpListener::bind(&addr)
        .await
        .expect("Failed to bind address");

    println!("✅ Rust 服务已启动: http://{}", addr);

    axum::serve(listener, app)
        .await
        .expect("Server failed to start");
}

async fn root() -> Json<ApiResponse<&'static str>> {
    Json(ApiResponse {
        code: 200,
        message: "Financial Kanban - Rust Service".to_string(),
        data: Some("0.1.0"),
    })
}

async fn health() -> Json<ApiResponse<&'static str>> {
    Json(ApiResponse {
        code: 200,
        message: "healthy".to_string(),
        data: Some("ok"),
    })
}
