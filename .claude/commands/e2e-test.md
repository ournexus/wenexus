---
description: 运行端到端测试，自动修复问题，重启应用并提供公网访问地址
---

## E2E 测试闭环流程

你需要完成以下闭环：**启动应用 → 运行测试 → 分析失败 → 修复代码 → 重启 → 重新测试 → 提供公网地址**

### 1. 确保应用运行

```bash
# 检查前端是否在运行
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
```

如果返回非 200，在项目根目录执行：

```bash
./scripts/dev.sh frontend
```

等待脚本输出公网地址。

### 2. 运行 E2E 测试

```bash
cd frontend
pnpm test:e2e
```

### 3. 分析测试结果

- 如果**全部通过**：跳到步骤 6
- 如果**有失败**：继续步骤 4

### 4. 分析失败原因并修复

1. 查看测试报告：

   ```bash
   cd frontend/packages/e2e
   cat test-results/.last-run.json 2>/dev/null || ls -la test-results/
   ```

2. 查看具体失败日志：

   ```bash
   ls -lt frontend/packages/e2e/test-results/ | head -10
   ```

3. 根据错误类型定位问题：
   - **元素找不到**：检查选择器是否正确，组件是否渲染
   - **超时**：检查网络请求、数据库连接
   - **断言失败**：检查业务逻辑

4. 修复代码后，继续步骤 5

### 5. 重启应用并重新测试

```bash
./scripts/dev.sh stop
./scripts/dev.sh frontend
```

等待启动完成后，回到步骤 2 重新运行测试。

**最多重试 3 次**。如果 3 次后仍失败，报告问题并请求用户协助。

### 6. 确认公网访问

测试全部通过后：

1. 获取公网地址：

   ```bash
   grep -o 'https://[^[:space:]]*\.trycloudflare\.com' scripts/logs/tunnel.log | tail -1
   ```

2. 验证公网可访问：

   ```bash
   PUBLIC_URL=$(grep -o 'https://[^[:space:]]*\.trycloudflare\.com' scripts/logs/tunnel.log | tail -1)
   curl -s -o /dev/null -w "%{http_code}" "$PUBLIC_URL"
   ```

3. 向用户报告：
   - ✅ E2E 测试全部通过
   - 🌐 公网访问地址：`$PUBLIC_URL`
   - 📋 测试覆盖的功能点

### 7. 日志位置速查

| 日志类型 | 路径 |
|---------|------|
| 前端日志 | `scripts/logs/frontend.log` |
| Tunnel 日志 | `scripts/logs/tunnel.log` |
| E2E 测试结果 | `frontend/packages/e2e/test-results/` |
| Playwright 报告 | `frontend/packages/e2e/playwright-report/` |

### 8. 常见问题排查

**Tunnel 断开**：

```bash
pkill -f cloudflared
cloudflared tunnel --url http://localhost:3000 > scripts/logs/tunnel.log 2>&1 &
sleep 5
grep -o 'https://[^[:space:]]*\.trycloudflare\.com' scripts/logs/tunnel.log | tail -1
```

**前端编译错误**：

```bash
tail -50 scripts/logs/frontend.log
```

**数据库连接问题**：

```bash
# 检查 PostgreSQL
brew services list | grep postgresql
# 检查 Redis
brew services list | grep redis
```

---

IMPORTANT:

- 每次修复后必须重新运行完整测试，不要跳过
- 修复代码时遵循项目现有风格
- 最终必须给用户一个可访问的公网地址

NEVER:

- 不要跳过测试直接说"已修复"
- 不要在没有验证的情况下声称公网可访问
- 不要超过 3 次重试仍继续循环
