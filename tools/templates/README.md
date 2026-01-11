# Module Templates

AI 和开发者创建新模块时使用的模板文件。

## 使用方法

### TypeScript 模块

复制 `module-ts.template` 内容到新模块的 `index.ts`：

```bash
cp tools/templates/module-ts.template frontend/packages/NEW_MODULE/src/index.ts
```

### Python 模块

复制 `module-py.template` 内容到新模块的 `__init__.py`：

```bash
cp tools/templates/module-py.template backend/python/src/NEW_MODULE/__init__.py
```

### package.json

复制 `package-json.template` 作为新包的基础：

```bash
cp tools/templates/package-json.template frontend/packages/NEW_MODULE/package.json
```

## 模板说明

| 模板 | 用途 | 必填字段 |
|------|------|----------|
| `module-ts.template` | TypeScript 模块入口 | @module, @description, @depends, @consumers |
| `module-py.template` | Python 模块入口 | 模块名, 描述, 依赖, 被依赖 |
| `package-json.template` | npm 包配置 | name, description |

## 检查

运行 `tools/scripts/check-module-docs.sh` 验证模块文档是否完整。
