# Install Guide

## How to install astral uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## How to install ollama and postgresql
```bash
sudo docker compose up -d
```

# Uv chinese doc
[link](https://hellowac.github.io/uv-zh-cn/)


# Road map
1. 建立llm模型  (完成)
2. 建立資料庫
3. 建立登入、註冊系統（auth）
4. 完成基本的chatbot （有記憶功能且區分使用者）
5. 加入RAG機制，來擴展llm
6. 加入爬蟲，來自動更新RAG資料庫