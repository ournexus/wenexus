# WeNexus Code Quality Standards

本文档定义了WeNexus项目的代码质量标准和最佳实践。

## Pre-commit Hooks

我们使用pre-commit来确保代码质量和一致性。所有代码在提交前都会自动进行检查和格式化。

### 安装Pre-commit

```bash
# 安装 pre-commit
pip install pre-commit

# 或者使用 npm
npm install -g pre-commit

# 在项目根目录安装 hooks
pre-commit install

# 安装 commit-msg hook（用于检查提交信息格式）
pre-commit install --hook-type commit-msg
```

### 手动运行检查

```bash
# 对所有文件运行检查
pre-commit run --all-files

# 对暂存的文件运行检查
pre-commit run

# 运行特定的hook
pre-commit run prettier --all-files
```

## 代码规范

### TypeScript/JavaScript

#### 格式化规则

- 使用Prettier进行代码格式化
- 缩进：2个空格
- 行宽：80字符
- 尾随逗号：ES5标准
- 单引号：优先使用单引号

#### ESLint规则

- 基于Next.js和TypeScript最佳实践
- 禁止使用`console.log`（除了测试文件）
- 要求显式的返回类型（对于导出的函数）
- 禁止使用`any`类型（除非有明确的类型注释）

#### 示例配置

```json
{
  "extends": ["next/core-web-vitals", "@typescript-eslint/recommended"],
  "rules": {
    "no-console": ["error", { "allow": ["warn", "error"] }],
    "@typescript-eslint/explicit-function-return-type": "error",
    "@typescript-eslint/no-explicit-any": "error"
  }
}
```

### Python

#### 格式化规则

- 使用Black进行代码格式化
- 行宽：88字符
- 使用isort进行import排序

#### Linting规则

- 使用flake8进行代码检查
- 使用mypy进行类型检查
- 所有公共函数必须有类型注解
- 所有模块必须有docstring

#### 示例

```python
"""WeNexus AI service module."""

from typing import List, Optional
import structlog

logger = structlog.get_logger()

def analyze_consensus(
    opinions: List[str],
    threshold: float = 0.8
) -> Optional[str]:
    """Analyze opinions to find consensus.

    Args:
        opinions: List of opinion strings
        threshold: Consensus threshold (0.0-1.0)

    Returns:
        Consensus statement if found, None otherwise
    """
    # Implementation here
    pass
```

### Java

#### 格式化规则

- 使用Google Java Format
- 缩进：2个空格
- 行宽：100字符

#### 代码风格

- 遵循Google Java Style Guide
- 所有公共方法必须有Javadoc
- 使用Optional处理可能为null的值

#### 示例

```java
/**
 * Service for managing consensus building processes.
 */
@Service
public class ConsensusService {

    /**
     * Builds consensus from multiple viewpoints.
     *
     * @param viewpoints List of viewpoints to analyze
     * @return Optional consensus result
     */
    public Optional<Consensus> buildConsensus(List<Viewpoint> viewpoints) {
        // Implementation here
        return Optional.empty();
    }
}
```

## 提交规范

### Conventional Commits

我们使用Conventional Commits规范来标准化提交信息：

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

#### 类型（Type）

- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式化（不影响功能）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `ci`: CI/CD相关
- `chore`: 构建工具、依赖管理等

#### 范围（Scope）- 可选

- `web`: Web应用
- `mobile`: 移动应用
- `admin`: 管理后台
- `api`: API相关
- `ai`: AI服务
- `auth`: 认证相关
- `ui`: UI组件
- `docs`: 文档

#### 示例

```bash
feat(web): add consensus visualization component

Add interactive star map for displaying expert opinions and consensus building process.

Closes #123
```

```bash
fix(api): resolve user authentication timeout issue

- Increase JWT token expiration time
- Add proper error handling for expired tokens
- Update authentication middleware

Fixes #456
```

## 安全检查

### 敏感信息检测

- 自动检测API密钥、密码等敏感信息
- 使用`.secrets.baseline`文件管理已知的安全例外

### 依赖安全

- 定期更新依赖包
- 使用`npm audit`和类似工具检查安全漏洞

## WeNexus特定规范

### 品牌一致性

- 始终使用"WeNexus"（大写W，大写N，无连字符）
- 避免使用"WeNexus"以外的变体形式

### 文档规范

- 所有公共API必须有完整的文档
- README文件必须保持更新
- 使用中英文双语注释（中文表达概念，英文表达技术细节）

### 测试要求

- 所有新功能必须有对应的测试
- 代码覆盖率不低于80%
- 集成测试覆盖核心用户流程

## 异常处理

### 跳过Pre-commit检查

在紧急情况下，可以跳过pre-commit检查：

```bash
# 跳过所有pre-commit hooks
git commit --no-verify -m "emergency fix"

# 或者设置环境变量
SKIP=no-console-logs git commit -m "allow console.log for debugging"
```

### 更新Hooks

```bash
# 更新所有hooks到最新版本
pre-commit autoupdate

# 清理并重新安装
pre-commit clean
pre-commit install
```

## 故障排除

### 常见问题

1. **Hook执行失败**

   ```bash
   # 检查具体错误
   pre-commit run --verbose

   # 重新安装hooks
   pre-commit uninstall
   pre-commit install
   ```

2. **格式化工具版本不一致**

   ```bash
   # 清理缓存
   pre-commit clean

   # 重新下载工具
   pre-commit run --all-files
   ```

3. **Node.js依赖问题**
   ```bash
   # 清理node_modules并重新安装
   rm -rf node_modules package-lock.json
   npm install
   ```

## 持续改进

我们定期审查和更新代码质量标准：

- 每季度审查pre-commit配置
- 根据团队反馈调整规则
- 关注社区最佳实践的发展

---

遵循这些标准将确保WeNexus代码库的高质量、一致性和可维护性。如有疑问，请在团队讨论中提出。
