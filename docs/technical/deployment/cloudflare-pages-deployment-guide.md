# Cloudflare Pages 部署最佳实践指南

## 1. 环境配置

### Node.js 版本管理

```bash
# .nvmrc
20.18.0
```

```bash
# .node-version
20.18.0
```

**最佳实践**:

- 使用 `.nvmrc` 和 `.node-version` 文件明确指定 Node.js 版本
- 选择与依赖兼容的 LTS 版本
- 定期更新到新的 LTS 版本以获取安全更新

### NPM 配置

```bash
# .npmrc
engine-strict=false
legacy-peer-deps=true
optional=true
```

**最佳实践**:

- `engine-strict=false`: 允许安装不完全匹配 engines 字段的包
- `legacy-peer-deps=true`: 解决复杂的依赖树冲突
- `optional=true`: 正确处理平台特定的可选依赖

## 2. 依赖管理

### 平台特定依赖

对于需要平台特定二进制模块的依赖（如 `@napi-rs/simple-git`），使用 `optionalDependencies`:

```json
"optionalDependencies": {
  "@napi-rs/simple-git-linux-x64-gnu": "0.1.19",
  "@napi-rs/simple-git-darwin-x64": "0.1.19",
  "@napi-rs/simple-git-win32-x64-msvc": "0.1.19"
}
```

**最佳实践**:

- 将平台特定依赖放在 `optionalDependencies` 而非 `dependencies`
- 确保版本号与主依赖版本匹配
- 包含所有可能的部署平台（Linux、macOS、Windows）

### 依赖版本冲突

解决依赖版本冲突使用 `overrides`:

```json
"overrides": {
  "yargs": "^18.0.0"
}
```

**最佳实践**:

- 确保 `overrides` 中的版本与直接依赖版本一致
- 解决冲突后运行 `npm install` 重新生成 lock 文件
- 避免过度使用 overrides，优先考虑升级依赖

### 安装脚本

添加 `postinstall` 脚本确保平台特定模块正确安装:

```json
"scripts": {
  "postinstall": "node -e \"try { require('@napi-rs/simple-git-linux-x64-gnu') } catch (e) { console.log('Platform-specific module not needed or already installed') }\""
}
```

**最佳实践**:

- 使用 `postinstall` 验证关键依赖安装
- 添加错误处理避免非关键错误中断构建
- 提供明确的日志信息便于调试

## 3. 构建配置

### 自定义构建脚本

```bash
#!/bin/bash
set -e

echo "Starting build process..."
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"
echo "Platform: $(uname -a)"

# 清理 npm 缓存避免问题
npm cache clean --force

# 安装依赖
echo "Installing dependencies..."
npm install --legacy-peer-deps --no-audit --no-fund

# 验证关键模块安装
if [ ! -d "node_modules/@napi-rs/simple-git-linux-x64-gnu" ] && [ "$(uname)" == "Linux" ]; then
  echo "Installing missing platform-specific module..."
  npm install @napi-rs/simple-git-linux-x64-gnu --legacy-peer-deps
fi

# 运行构建
echo "Running build..."
npm run build

echo "Build completed successfully!"
```

**最佳实践**:

- 使用 `set -e` 确保任何错误都会终止脚本
- 输出环境信息便于调试
- 添加平台检测逻辑针对性处理依赖
- 提供清晰的构建步骤日志

### Cloudflare Pages 配置

在 Cloudflare Pages 控制台配置:

- **构建命令**: `chmod +x ./build.sh && ./build.sh`
- **构建输出目录**: `public`
- **环境变量**:
  - `NODE_VERSION`: `20.18.0`
  - `NPM_FLAGS`: `--legacy-peer-deps`

**最佳实践**:

- 使用自定义构建脚本而非默认命令
- 确保脚本有执行权限
- 明确指定输出目录
- 设置必要的环境变量

## 4. 部署前检查清单

每次部署前检查:

1. **依赖同步**: 确保 `package.json` 和 `package-lock.json` 完全同步

   ```bash
   npm install --legacy-peer-deps
   git add package-lock.json
   git commit -m "Update package-lock.json"
   ```

2. **版本兼容性**: 检查依赖的 Node.js 版本要求与部署环境匹配

   ```bash
   npm ls
   ```

3. **构建测试**: 在本地测试构建过程

   ```bash
   ./build.sh
   ```

4. **文件权限**: 确保构建脚本有执行权限

   ```bash
   chmod +x ./build.sh
   ```

5. **Git 提交**: 确保所有更改都已提交并推送
   ```bash
   git status
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

## 5. 故障排除

### 常见错误与解决方案

1. **npm ci 失败**:
   - 错误: `Missing: @package-name from lock file`
   - 解决: 运行 `npm install` 更新 lock 文件

2. **平台特定模块缺失**:
   - 错误: `Cannot find module '@napi-rs/simple-git-linux-x64-gnu'`
   - 解决: 添加到 `optionalDependencies` 并更新 lock 文件

3. **Node.js 版本不兼容**:
   - 错误: `Unsupported engine { package: 'package-name', required: { node: '^version' } }`
   - 解决: 更新 `.nvmrc` 和 `.node-version` 到兼容版本

4. **构建命令失败**:
   - 检查 Cloudflare Pages 构建日志
   - 确保构建脚本有执行权限
   - 验证环境变量设置正确

### 调试技巧

1. 在构建脚本中添加详细日志
2. 使用 `npm install --verbose` 查看详细安装过程
3. 检查 Cloudflare Pages 构建日志中的错误信息
4. 在本地复制 Cloudflare 环境进行测试

## 6. 持续集成最佳实践

1. **自动化测试**: 在推送前运行测试确保代码质量
2. **依赖审计**: 定期运行 `npm audit` 检查安全漏洞
3. **版本锁定**: 使用精确版本号避免意外更新
4. **分支策略**: 使用开发分支进行测试，主分支用于生产部署
5. **部署预览**: 利用 Cloudflare Pages 的预览功能测试变更
