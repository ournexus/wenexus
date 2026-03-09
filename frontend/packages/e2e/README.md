# @wenexus/e2e

End-to-end tests for WeNexus applications using Playwright.

## Structure

```
packages/e2e/
├── fixtures/          # Page Objects 和测试工具
│   ├── auth.ts        # 认证相关
│   └── index.ts
├── tests/             # 测试用例
│   └── auth/          # 认证测试
└── playwright.config.ts
```

## Usage

```bash
# 确保 web 应用已启动
pnpm --filter @wenexus/web dev

# 运行测试
pnpm --filter @wenexus/e2e test

# UI 模式
pnpm --filter @wenexus/e2e test:ui

# 带浏览器界面
pnpm --filter @wenexus/e2e test:headed

# 查看报告
pnpm --filter @wenexus/e2e report
```

## Adding Tests

1. 在 `fixtures/` 中创建 Page Object
2. 在 `tests/` 中创建测试文件
3. 从 `../../fixtures` 导入工具
