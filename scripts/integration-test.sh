#!/bin/bash

# 集成测试脚本
# 用于验证所有服务的集成情况

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 服务配置
PYTHON_SERVICE_URL="http://localhost:8000"
NODE_SERVICE_URL="http://localhost:3000"
RUST_SERVICE_URL="http://localhost:8080"
FRONTEND_URL="http://localhost:3001"

# 测试结果
PASSED=0
FAILED=0

# 打印测试结果
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $2"
        ((FAILED++))
    fi
}

# 检查服务是否运行
check_service() {
    local url=$1
    local name=$2
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 测试 API 端点
test_api_endpoint() {
    local method=$1
    local url=$2
    local data=$3
    local expected_code=${4:-200}
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq "$expected_code" ]; then
        return 0
    else
        echo "  Expected HTTP $expected_code, got $http_code"
        echo "  Response: $body"
        return 1
    fi
}

echo "=========================================="
echo "  集成测试开始"
echo "=========================================="
echo ""

# 1. 检查 MongoDB
echo "1. 检查 MongoDB 连接..."
if nc -z localhost 27017 2>/dev/null; then
    print_result 0 "MongoDB 端口 27017 可访问"
else
    print_result 1 "MongoDB 端口 27017 不可访问（请先启动 MongoDB）"
fi
echo ""

# 2. 检查 Python 服务
echo "2. 检查 Python 服务..."
if check_service "$PYTHON_SERVICE_URL/" "Python 服务"; then
    print_result 0 "Python 服务运行正常"
    
    # 测试 CRUD 操作
    echo "  测试 Python 服务 API..."
    
    # 创建 Item
    create_response=$(curl -s -X POST "$PYTHON_SERVICE_URL/api/v1/items" \
        -H "Content-Type: application/json" \
        -d '{"name": "测试项目", "description": "集成测试", "amount": 100.0}')
    item_id=$(echo "$create_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$item_id" ]; then
        print_result 0 "  POST /api/v1/items - 创建成功"
        
        # 获取所有 Items
        if test_api_endpoint "GET" "$PYTHON_SERVICE_URL/api/v1/items"; then
            print_result 0 "  GET /api/v1/items - 获取列表成功"
        else
            print_result 1 "  GET /api/v1/items - 获取列表失败"
        fi
        
        # 获取单个 Item
        if test_api_endpoint "GET" "$PYTHON_SERVICE_URL/api/v1/items/$item_id"; then
            print_result 0 "  GET /api/v1/items/{id} - 获取单个成功"
        else
            print_result 1 "  GET /api/v1/items/{id} - 获取单个失败"
        fi
        
        # 更新 Item
        if test_api_endpoint "PUT" "$PYTHON_SERVICE_URL/api/v1/items/$item_id" \
            '{"name": "更新后的项目", "description": "更新描述", "amount": 200.0}'; then
            print_result 0 "  PUT /api/v1/items/{id} - 更新成功"
        else
            print_result 1 "  PUT /api/v1/items/{id} - 更新失败"
        fi
        
        # 删除 Item
        if test_api_endpoint "DELETE" "$PYTHON_SERVICE_URL/api/v1/items/$item_id"; then
            print_result 0 "  DELETE /api/v1/items/{id} - 删除成功"
        else
            print_result 1 "  DELETE /api/v1/items/{id} - 删除失败"
        fi
    else
        print_result 1 "  POST /api/v1/items - 创建失败"
    fi
else
    print_result 1 "Python 服务未运行（请先启动服务）"
fi
echo ""

# 3. 检查 Node.js 服务
echo "3. 检查 Node.js 服务..."
if check_service "$NODE_SERVICE_URL/api/v1/" "Node.js 服务"; then
    print_result 0 "Node.js 服务运行正常"
    
    # 测试 CRUD 操作
    echo "  测试 Node.js 服务 API..."
    
    # 创建 Item
    create_response=$(curl -s -X POST "$NODE_SERVICE_URL/api/v1/items" \
        -H "Content-Type: application/json" \
        -d '{"name": "测试项目", "description": "集成测试", "amount": 100.0}')
    item_id=$(echo "$create_response" | grep -o '"_id":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$item_id" ]; then
        print_result 0 "  POST /api/v1/items - 创建成功"
        
        # 获取所有 Items
        if test_api_endpoint "GET" "$NODE_SERVICE_URL/api/v1/items"; then
            print_result 0 "  GET /api/v1/items - 获取列表成功"
        else
            print_result 1 "  GET /api/v1/items - 获取列表失败"
        fi
        
        # 获取单个 Item
        if test_api_endpoint "GET" "$NODE_SERVICE_URL/api/v1/items/$item_id"; then
            print_result 0 "  GET /api/v1/items/{id} - 获取单个成功"
        else
            print_result 1 "  GET /api/v1/items/{id} - 获取单个失败"
        fi
        
        # 更新 Item
        if test_api_endpoint "PUT" "$NODE_SERVICE_URL/api/v1/items/$item_id" \
            '{"name": "更新后的项目", "description": "更新描述", "amount": 200.0}'; then
            print_result 0 "  PUT /api/v1/items/{id} - 更新成功"
        else
            print_result 1 "  PUT /api/v1/items/{id} - 更新失败"
        fi
        
        # 删除 Item
        if test_api_endpoint "DELETE" "$NODE_SERVICE_URL/api/v1/items/$item_id"; then
            print_result 0 "  DELETE /api/v1/items/{id} - 删除成功"
        else
            print_result 1 "  DELETE /api/v1/items/{id} - 删除失败"
        fi
    else
        print_result 1 "  POST /api/v1/items - 创建失败"
    fi
else
    print_result 1 "Node.js 服务未运行（请先启动服务）"
fi
echo ""

# 4. 检查 Rust 服务
echo "4. 检查 Rust 服务..."
if check_service "$RUST_SERVICE_URL/health" "Rust 服务"; then
    print_result 0 "Rust 服务运行正常"
    
    # 测试 CRUD 操作
    echo "  测试 Rust 服务 API..."
    
    # 创建 Item
    create_response=$(curl -s -X POST "$RUST_SERVICE_URL/api/v1/items" \
        -H "Content-Type: application/json" \
        -d '{"name": "测试项目", "description": "集成测试", "amount": 100.0}')
    item_id=$(echo "$create_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$item_id" ]; then
        print_result 0 "  POST /api/v1/items - 创建成功"
        
        # 获取所有 Items
        if test_api_endpoint "GET" "$RUST_SERVICE_URL/api/v1/items"; then
            print_result 0 "  GET /api/v1/items - 获取列表成功"
        else
            print_result 1 "  GET /api/v1/items - 获取列表失败"
        fi
        
        # 获取单个 Item
        if test_api_endpoint "GET" "$RUST_SERVICE_URL/api/v1/items/$item_id"; then
            print_result 0 "  GET /api/v1/items/{id} - 获取单个成功"
        else
            print_result 1 "  GET /api/v1/items/{id} - 获取单个失败"
        fi
        
        # 更新 Item
        if test_api_endpoint "PUT" "$RUST_SERVICE_URL/api/v1/items/$item_id" \
            '{"name": "更新后的项目", "description": "更新描述", "amount": 200.0}'; then
            print_result 0 "  PUT /api/v1/items/{id} - 更新成功"
        else
            print_result 1 "  PUT /api/v1/items/{id} - 更新失败"
        fi
        
        # 删除 Item
        if test_api_endpoint "DELETE" "$RUST_SERVICE_URL/api/v1/items/$item_id"; then
            print_result 0 "  DELETE /api/v1/items/{id} - 删除成功"
        else
            print_result 1 "  DELETE /api/v1/items/{id} - 删除失败"
        fi
    else
        print_result 1 "  POST /api/v1/items - 创建失败"
    fi
else
    print_result 1 "Rust 服务未运行（请先启动服务）"
fi
echo ""

# 5. 检查前端服务
echo "5. 检查前端服务..."
if check_service "$FRONTEND_URL" "前端服务"; then
    print_result 0 "前端服务运行正常"
else
    print_result 1 "前端服务未运行（请先启动服务）"
fi
echo ""

# 总结
echo "=========================================="
echo "  测试结果汇总"
echo "=========================================="
echo -e "${GREEN}通过: $PASSED${NC}"
echo -e "${RED}失败: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}所有测试通过！${NC}"
    exit 0
else
    echo -e "${YELLOW}部分测试失败，请检查服务状态和配置${NC}"
    exit 1
fi
