# Code Inspector 集成说明

本项目已准备集成 [Code Inspector](https://inspector.fe-dev.cn/) 用于开发调试。

## 当前状态

⚠️ **注意**: `code-inspector-plugin` 目前与本项目的 esbuild 配置存在兼容性问题。插件尝试访问 Node.js
fs API 时出现错误。

## 使用方法

### 推荐：增强开发模式

```bash
npm run dev:client
```

这将启动一个专门用于客户端开发的服务器，支持：

- 实时热重载
- 完整的源码映射 (inline sourcemaps)
- 构建元信息生成
- 在 `http://localhost:3000` 提供服务

### 常规开发模式

```bash
npm run dev
```

这将启动完整的 Cloudflare Worker 开发环境。

## 当前可用的调试功能

### 浏览器开发者工具

- 完整的源码映射支持
- 可以直接在 TypeScript 源码上设置断点
- 变量检查和调用栈追踪
- 性能分析和内存分析

### 热重载开发

- 文件更改时自动重新构建
- 浏览器自动刷新
- 快速开发迭代

## 解决方案状态

### 已尝试的解决方案

1. ✅ 安装了 `code-inspector-plugin`
2. ❌ 直接集成到 esbuild 构建 - fs API 访问问题
3. ❌ 独立开发服务器模式 - 同样的 fs API 问题
4. ✅ 降级到增强开发模式（当前方案）

### 未来改进

- 等待插件更新解决 esbuild 兼容性
- 考虑使用其他源码映射和调试工具
- 可能需要切换到 Vite 或 Webpack 来支持完整的 Code Inspector 功能

## 替代调试方案

由于 Code Inspector 暂时不可用，建议使用以下调试方法：

1. **浏览器开发者工具**: 完整的源码映射支持
2. **VS Code 调试器**: 配置 Chrome 调试器连接
3. **React DevTools**: 如果使用 React 组件
4. **console.log**: 传统但有效的调试方法

## 技术细节

当前遇到的错误：

```
Cannot read properties of undefined (reading 'readFile')
```

这表明插件在尝试读取文件系统时，Node.js 的 `fs.promises.readFile` API 未正确可用，可能是由于：

- esbuild 插件环境限制
- Node.js 版本兼容性
- 插件本身的实现问题
