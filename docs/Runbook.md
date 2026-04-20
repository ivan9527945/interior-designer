# RenderStudio 值班手冊（Runbook）

## 系統架構摘要

RenderStudio 由三層組成：**前端**（Next.js，部署於 Vercel 或自建容器）、**後端 API**（FastAPI，透過 Docker Compose 運行）、以及**本機 Agent**（設計師端 Python 程序，負責與 SketchUp/V-Ray 互動並上傳結果）。渲染任務透過後端 API 建立後，存入資料庫佇列，Agent 輪詢後執行渲染，完成後將輸出檔案上傳至 MinIO 物件儲存，並回報狀態至後端。Grafana 串接 Prometheus `/metrics` 提供監控告警。

---

## 常見問題排查

### Q1：Agent 離線（Dashboard 顯示「Agent 未連線」）

1. 在設計師電腦確認 Agent 程序是否在執行：
   ```
   ps aux | grep render_agent
   ```
2. 若未執行，重新啟動：
   ```
   cd ~/renderstudio-agent && python agent_main.py
   ```
3. 確認 `RENDERSTUDIO_API_BASE` 環境變數指向正確後端 URL，且網路可連線。
4. 查看 `~/renderstudio-agent/agent.log` 尋找錯誤訊息，常見原因：API Token 過期、後端 URL 錯誤。

### Q2：渲染 Queue 塞住（任務長時間停在 `queued`）

1. 確認 Agent 是否在線（參考 Q1）。
2. 連線後端，檢查資料庫中佇列狀態：
   ```
   docker compose exec db psql -U postgres -d renderstudio \
     -c "SELECT id, status, created_at FROM renders WHERE status='queued' ORDER BY created_at LIMIT 10;"
   ```
3. 若有任務卡超過 30 分鐘，手動將其標為 `failed` 並通知使用者重新送出：
   ```sql
   UPDATE renders SET status='failed', error_message='Queue timeout – resubmit'
   WHERE status='queued' AND created_at < NOW() - INTERVAL '30 minutes';
   ```
4. 重啟 Agent 後觀察佇列是否恢復消化。

### Q3：MinIO 連不上（上傳或下載失敗，HTTP 502/503）

1. 確認 MinIO 容器是否正常運行：
   ```
   docker compose ps minio
   ```
2. 若容器停止，重啟：
   ```
   docker compose up -d minio
   ```
3. 進入 MinIO 主控台（預設 `http://localhost:9001`）確認 Bucket `renderstudio` 是否存在且權限正確。
4. 確認 `MINIO_ROOT_USER` 及 `MINIO_ROOT_PASSWORD` 環境變數與後端設定一致。

### Q4：API 返回 503（後端服務不可用）

1. 確認後端容器狀態：
   ```
   docker compose ps api
   ```
2. 查看容器日誌：
   ```
   docker compose logs --tail=100 api
   ```
3. 若為 OOM 被 kill，增加 `docker-compose.yml` 中 `api` 服務的 `mem_limit` 後重啟。
4. 重啟後端：
   ```
   docker compose restart api
   ```

---

## 重啟服務命令

### Docker Compose（本地 / VM 環境）

```bash
# 重啟所有服務
docker compose restart

# 重啟單一服務
docker compose restart api
docker compose restart db
docker compose restart minio

# 完整停止再啟動（保留資料 volume）
docker compose down && docker compose up -d
```

### Kubernetes（正式環境）

```bash
# 重啟 API Deployment
kubectl rollout restart deployment/renderstudio-api -n renderstudio

# 查看 rollout 狀態
kubectl rollout status deployment/renderstudio-api -n renderstudio

# 強制重新拉取 image（更新版本後）
kubectl set image deployment/renderstudio-api api=registry.internal/renderstudio-api:latest -n renderstudio
```

---

## 備份與還原

### 資料庫備份

```bash
# 建立備份（存入 ./backups/）
docker compose exec db pg_dump -U postgres renderstudio \
  > backups/renderstudio_$(date +%Y%m%d_%H%M%S).sql
```

### 資料庫還原

```bash
# 還原（會覆蓋現有資料，請先確認備份檔正確）
docker compose exec -T db psql -U postgres renderstudio \
  < backups/renderstudio_YYYYMMDD_HHMMSS.sql
```

### MinIO 備份

使用 `mc`（MinIO Client）將 Bucket 同步至外部儲存：

```bash
mc mirror minio/renderstudio /mnt/backup/minio-renderstudio/
```

---

## Grafana 告警對應處理

| 告警名稱 | 嚴重度 | 處理步驟 |
|---|---|---|
| `renderstudio_up == 0` | 緊急 | 後端 API 已停止回應，立即依 Q4 步驟重啟 API 容器 |
| `render_queue_depth > 20` | 警告 | 渲染佇列積壓，檢查 Agent 是否在線（Q1、Q2） |
| `minio_disk_used_percent > 85` | 警告 | MinIO 磁碟空間不足，清理 30 天以上舊渲染檔或擴充 Volume |
| `api_p99_latency > 3s` | 警告 | API 回應慢，查看 slow query log，考慮增加 DB 索引或重啟服務 |
| `db_connection_pool_exhausted` | 緊急 | DB 連線池耗盡，重啟 API（`docker compose restart api`）並增加 `DATABASE_POOL_SIZE` |
