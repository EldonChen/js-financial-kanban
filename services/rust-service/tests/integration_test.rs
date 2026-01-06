// 集成测试文件
// 这些测试需要真实的 MongoDB 连接

#[cfg(test)]
mod integration_tests {
    #[tokio::test]
    #[ignore] // 默认忽略，需要 MongoDB 时使用 --ignored 运行
    async fn test_items_crud_flow() {
        // 这个测试需要真实的 MongoDB 连接
        // 运行: cargo test -- --ignored
        // 暂时跳过，等待 MongoDB 连接配置
    }
}
