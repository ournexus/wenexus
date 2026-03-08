# E2E Tests — WeNexus Web App

## 测试分层

```
e2e/
├── health/            # 应用健康检查（Playwright 自动化，CI 可跑）
│   ├── app-startup    # 应用启动、无致命错误
│   ├── api-routes     # API 端点可达、不崩溃
│   └── page-routes    # 页面路由返回 200、不白屏
├── cases/             # 语义化业务用例（YAML 描述，人/AI 可执行）
│   ├── core-flow      # P0 核心闭环
│   ├── discovery      # 话题管理与信息流
│   ├── roundtable     # 圆桌讨论
│   ├── deliverable    # 交付物生成
│   └── identity       # 用户偏好
└── playwright.config.ts
```

## 运行方式

```bash
# 运行健康检查（CI 用）
pnpm test:e2e

# UI 模式调试
pnpm test:e2e:ui
```

## 语义用例

`cases/` 下的 YAML 文件描述业务行为和验证点，不包含 DOM 选择器。

执行方式：

- **AI 执行**：模型读取 YAML，通过浏览器按步骤操作
- **自动化执行**：UI 稳定后根据用例补充 Playwright spec
