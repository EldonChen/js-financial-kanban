use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use mongodb::bson::oid::ObjectId;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Item {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub price: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub created_at: Option<DateTime<Utc>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub updated_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Deserialize)]
pub struct CreateItemRequest {
    pub name: String,
    pub description: Option<String>,
    pub price: Option<f64>,
}

#[derive(Debug, Deserialize)]
pub struct UpdateItemRequest {
    pub name: Option<String>,
    pub description: Option<String>,
    pub price: Option<f64>,
}

#[derive(Debug, Serialize)]
pub struct ItemResponse {
    pub id: String,
    pub name: String,
    pub description: Option<String>,
    pub price: Option<f64>,
    pub created_at: String,
    pub updated_at: String,
}

impl From<Item> for ItemResponse {
    fn from(item: Item) -> Self {
        ItemResponse {
            id: item.id.map(|id| id.to_hex()).unwrap_or_default(),
            name: item.name,
            description: item.description,
            price: item.price,
            created_at: item.created_at
                .map(|dt| dt.to_rfc3339())
                .unwrap_or_default(),
            updated_at: item.updated_at
                .map(|dt| dt.to_rfc3339())
                .unwrap_or_default(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct ApiResponse<T> {
    pub code: u16,
    pub message: String,
    pub data: Option<T>,
}

impl<T> ApiResponse<T> {
    pub fn success(data: T) -> Self {
        Self {
            code: 200,
            message: "success".to_string(),
            data: Some(data),
        }
    }

    pub fn error(message: String, code: u16) -> Self {
        Self {
            code,
            message,
            data: None,
        }
    }
}
