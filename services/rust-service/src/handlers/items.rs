use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::Json,
};
use chrono::Utc;
use mongodb::{Database, bson::{doc, oid::ObjectId, DateTime as BsonDateTime}};
use futures::stream::TryStreamExt;
use crate::models::item::{
    ApiResponse, CreateItemRequest, Item, ItemResponse, UpdateItemRequest,
};

pub async fn get_items(State(db): State<Database>) -> Result<Json<ApiResponse<Vec<ItemResponse>>>, StatusCode> {
    let collection = db.collection::<Item>("items");
    let mut items = Vec::new();

    match collection.find(doc! {}).await {
        Ok(mut cursor) => {
            while let Ok(Some(item)) = cursor.try_next().await {
                items.push(ItemResponse::from(item));
            }
            Ok(Json(ApiResponse::success(items)))
        }
        Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
    }
}

pub async fn get_item(
    Path(id): Path<String>,
    State(db): State<Database>,
) -> Result<Json<ApiResponse<ItemResponse>>, StatusCode> {
    let object_id = match ObjectId::parse_str(&id) {
        Ok(id) => id,
        Err(_) => return Err(StatusCode::BAD_REQUEST),
    };

    let collection = db.collection::<Item>("items");
    match collection.find_one(doc! { "_id": object_id }).await {
        Ok(Some(item)) => Ok(Json(ApiResponse::success(ItemResponse::from(item)))),
        Ok(None) => Err(StatusCode::NOT_FOUND),
        Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
    }
}

pub async fn create_item(
    State(db): State<Database>,
    Json(payload): Json<CreateItemRequest>,
) -> Result<Json<ApiResponse<ItemResponse>>, StatusCode> {
    let now = Utc::now();
    let item = Item {
        id: None,
        name: payload.name,
        description: payload.description,
        price: payload.price,
        created_at: Some(now),
        updated_at: Some(now),
    };

    let collection = db.collection::<Item>("items");
    match collection.insert_one(&item).await {
        Ok(result) => {
            if let Some(inserted_id) = result.inserted_id.as_object_id() {
                match collection.find_one(doc! { "_id": inserted_id }).await {
                    Ok(Some(item)) => Ok(Json(ApiResponse::success(ItemResponse::from(item)))),
                    _ => Err(StatusCode::INTERNAL_SERVER_ERROR),
                }
            } else {
                Err(StatusCode::INTERNAL_SERVER_ERROR)
            }
        }
        Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
    }
}

pub async fn update_item(
    Path(id): Path<String>,
    State(db): State<Database>,
    Json(payload): Json<UpdateItemRequest>,
) -> Result<Json<ApiResponse<ItemResponse>>, StatusCode> {
    let object_id = match ObjectId::parse_str(&id) {
        Ok(id) => id,
        Err(_) => return Err(StatusCode::BAD_REQUEST),
    };

    let collection = db.collection::<Item>("items");
    
    // 检查 item 是否存在
    match collection.find_one(doc! { "_id": object_id }).await {
        Ok(None) => return Err(StatusCode::NOT_FOUND),
        Err(_) => return Err(StatusCode::INTERNAL_SERVER_ERROR),
        Ok(_) => {}
    }

    // 构建更新文档
    let mut update_doc = doc! {};
    if let Some(name) = payload.name {
        update_doc.insert("name", name);
    }
    if let Some(description) = payload.description {
        update_doc.insert("description", description);
    }
    if let Some(price) = payload.price {
        update_doc.insert("price", price);
    }
    update_doc.insert("updated_at", BsonDateTime::now());

    match collection
        .update_one(doc! { "_id": object_id }, doc! { "$set": update_doc })
        .await
    {
        Ok(_) => {
            match collection.find_one(doc! { "_id": object_id }).await {
                Ok(Some(item)) => Ok(Json(ApiResponse::success(ItemResponse::from(item)))),
                _ => Err(StatusCode::INTERNAL_SERVER_ERROR),
            }
        }
        Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use mongodb::bson::oid::ObjectId;

    #[tokio::test]
    async fn test_get_item_invalid_id() {
        // 测试无效 ID 格式
        let fake_id = "invalid-id".to_string();
        // 这个测试主要验证错误处理逻辑
        // 实际数据库操作需要真实 MongoDB 或 mock
        assert!(ObjectId::parse_str(&fake_id).is_err());
    }
}

pub async fn delete_item(
    Path(id): Path<String>,
    State(db): State<Database>,
) -> Result<Json<ApiResponse<()>>, StatusCode> {
    let object_id = match ObjectId::parse_str(&id) {
        Ok(id) => id,
        Err(_) => return Err(StatusCode::BAD_REQUEST),
    };

    let collection = db.collection::<Item>("items");
    match collection.delete_one(doc! { "_id": object_id }).await {
        Ok(result) => {
            if result.deleted_count > 0 {
                Ok(Json(ApiResponse::success(())))
            } else {
                Err(StatusCode::NOT_FOUND)
            }
        }
        Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
    }
}
