---
name: xiaohongshu
description: 小红书全能助手 — 文案生成、封面制作、内容发布与管理。当用户要求写小红书笔记、生成小红书文案/标题/封面、发小红书、搜索小红书、评论点赞收藏等任何小红书相关操作时使用。支持一站式从文案创作到自动发布的完整流程。封面AI生图需配置可选环境变量（GEMINI_API_KEY 或 IMG_API_KEY 或 HUNYUAN_SECRET_ID+KEY）。
metadata: {"openclaw": {"emoji": "📕", "requires": {"bins": [], "anyBins": ["curl"]}}}
---

# 📕 小红书全能助手

两大核心能力：**文案创作**（标题+正文+封面图）和 **平台操作**（发布+搜索+互动）。

文案创作默认使用当前对话的主模型，无需额外配置。
平台操作通过 **Chrome DevTools MCP** 在 Mac 本地浏览器中执行。

---

## 一、文案创作流程

当用户要求写笔记、生成文案、创作小红书内容时，按 **标题 → 正文 → 封面图** 三步执行，每步需用户确认后再继续。

### 1.1 生成标题

**优先使用当前对话模型直接生成**，参考 [references/title-guide.md]({baseDir}/references/title-guide.md) 中的规范生成5个不同风格的标题。

核心要求：每个标题使用不同风格，20字以内，含1-2个emoji，禁用平台禁忌词。

**备用方案**：如果用户明确配置了 `XHS_AI_API_KEY` 环境变量并要求使用指定 API，可调用脚本：
```bash
bash {baseDir}/scripts/generate.sh title "内容摘要"
```

**输出后询问用户**：选择哪个标题？可修改或自定义。默认选第一个。

### 1.2 生成正文

**优先使用当前对话模型直接生成**，参考 [references/content-guide.md]({baseDir}/references/content-guide.md) 中的规范，根据选定标题生成正文。

核心要求：600-800字，像朋友聊天的语气，禁用列表/编号，用自然段落呈现，文末5-10个#标签。

**备用方案**：如果用户明确配置了 `XHS_AI_API_KEY` 环境变量并要求使用指定 API，可调用脚本：
```bash
bash {baseDir}/scripts/generate.sh content "完整内容" "选定标题"
```

**输出后询问用户**：是否满意？可要求修改。确认后进入封面图步骤。

### 1.3 生成封面图

封面图结构：1080x1440（3:4），上半部分为主题图片（1080x720），下半部分为纯色底+标题文字（1080x720）。

#### 1.3.1 询问用户选择封面图片来源

**必须先询问用户**：

> 封面图的主题图片，你想怎么来？
> 1. **AI 自动生成** — 根据文案主题自动生成匹配的图片
> 2. **上传自己的图片** — 提供图片路径，我来帮你拼接封面

#### 1.3.2A 用户选择「AI生成」

**继续询问 prompt 方式**：

> AI图片的提示词，你想怎么来？
> 1. **预设推荐** — 我根据你的文案主题自动生成最佳英文prompt
> 2. **自定义提示词** — 你提供想要的画面描述，我来翻译成英文prompt

**预设推荐**：Agent 参考 [references/cover-guide.md]({baseDir}/references/cover-guide.md) 自动生成英文 prompt，展示给用户确认后执行。

**自定义提示词**：用户描述画面，Agent 翻译/优化为英文 prompt，展示确认后执行。

确认 prompt 后，根据主题从 [references/cover-guide.md]({baseDir}/references/cover-guide.md) 配色库选择底色和字色（必须主动搭配，禁止白底黑字）。

##### 生图模型选择策略

**优先尝试当前对话使用的模型**直接生图（如果当前模型支持图片生成）。Agent 在自己的对话环境中直接调用生图能力：
1. 生成 3:2 比例的主题图片，保存到临时文件（如 `/tmp/xhs_ai_img.png`）
2. 然后调用 cover.sh 时传入 `__USER_IMAGE__:/tmp/xhs_ai_img.png`，跳过脚本内置的 API 调用

**如果当前模型不支持生图**（生成失败或明确不具备图片生成能力），**询问用户**：

> 当前模型不支持图片生成，请选择生图方式：
> 1. **Google Gemini** — 需要提供 GEMINI_API_KEY（[获取地址](https://aistudio.google.com/apikey)）
> 2. **OpenAI / OpenAI兼容API** — 需要提供 API Key 和 Base URL
> 3. **其他方式** — 你来提供图片，我帮你拼接封面

用户选择后，设置对应的环境变量再调用 cover.sh：

- **Gemini**：`GEMINI_API_KEY=xxx bash cover.sh "标题" "prompt" ...`
- **OpenAI兼容**：`IMG_API_TYPE=openai IMG_API_KEY=xxx IMG_API_BASE=https://api.openai.com/v1 IMG_MODEL=dall-e-3 bash cover.sh "标题" "prompt" ...`
- **腾讯云混元生图（AIART）**：`IMG_API_TYPE=hunyuan HUNYUAN_SECRET_ID=AKID... HUNYUAN_SECRET_KEY=... bash cover.sh "标题" "prompt" ...`
- **其他方式**：用户提供图片路径，走 `__USER_IMAGE__` 模式

直接调用 cover.sh 的命令格式（仅当需要脚本内置 API 生图时）：

```bash
bash {baseDir}/scripts/cover.sh "标题文字" "英文prompt" [输出路径] [底色hex] [字色hex]
```

#### 1.3.2B 用户选择「上传图片」

用户提供图片路径后，同样搭配底色和字色，执行：

```bash
bash {baseDir}/scripts/cover.sh "标题文字" "__USER_IMAGE__:/path/to/image.jpg" [输出路径] [底色hex] [字色hex]
```

#### 封面图前置要求

- ImageMagick（`magick`）或 Pillow（`pip install Pillow`）
- 中文字体（Mac 系统自带 PingFang/STHeiti，推荐安装阿里巴巴普惠体）
- 安装 ImageMagick：`brew install imagemagick`

### 1.4 文案完成后

询问用户是否要直接发布到小红书。如果要发布，自动进入下方「平台操作」的发布流程。

---

## 二、平台操作

当用户要求发帖、搜索、浏览、互动等小红书操作时使用。所有操作通过 **Chrome DevTools MCP** 在本地 Chrome 浏览器中执行。

### 2.1 前置检查

每次操作前必须先执行：

```bash
bash {baseDir}/check_env.sh
```

返回码：`0` = 环境就绪；`1` = Chrome 未安装；`2` = 无图像工具（不影响发布，仅影响封面生成）。

### 2.2 确保 Chrome 调试模式

```bash
bash {baseDir}/scripts/ensure-chrome-debug.sh
```

这会启动带 `--remote-debugging-port=9222` 的 Chrome，复用用户原有登录状态。

### 2.3 Chrome DevTools 工具映射

以下是所有可用操作及其 Chrome DevTools MCP 工具调用方式。参考 [references/web-structure.md]({baseDir}/references/web-structure.md) 了解页面结构，参考 [references/workflow.md]({baseDir}/references/workflow.md) 了解发布 SOP。

#### 1. 打开小红书
```
navigate_page → url: https://www.xiaohongshu.com/explore
```

#### 2. 检查登录状态
```javascript
// evaluate_script
() => {
  const links = document.querySelectorAll('a');
  for (const a of links) {
    if (a.textContent.includes('我')) return { loggedIn: true };
  }
  return { loggedIn: false };
}
```

#### 3. 登录流程

**方式一：浏览器扫码**
```
navigate_page → url: https://www.xiaohongshu.com
take_snapshot → 找到"登录"按钮 → click
take_screenshot → 展示二维码给用户扫码
```

**方式二：手机号登录**
```
take_snapshot → 找到手机号输入框
fill → 输入手机号
click → 点击"获取验证码"
// 询问用户验证码
fill → 输入验证码
click → 点击"登录"
```

#### 4. 发布图文内容（两种模式）

详见 [references/workflow.md]({baseDir}/references/workflow.md)。

**Mode A: 自定义封面图上传**
1. 导航到创作中心：`navigate_page → url: https://creator.xiaohongshu.com/publish/publish`
2. 点击"上传图文"
3. `upload_file` 上传封面图（如 `/tmp/xhs_cover.png`）
4. 等待处理 → 点击"下一步"
5. 填写标题（nativeInputValueSetter 模式，见 workflow.md）
6. 发布 → 验证 URL 包含 `published=true`

**Mode B: 文字配图（平台生成图片）**
1. 导航到创作中心
2. 点击"上传图文" → 点击"文字配图"
3. 用 ClipboardEvent 粘贴内容到 `.tiptap.ProseMirror` 编辑器
4. 点击"生成图片" → 等待预览
5. "下一步" → 填写标题 → 发布

#### 5. 搜索内容
```
navigate_page → url: https://www.xiaohongshu.com/explore
take_snapshot → 找到搜索框 → fill(keyword)
press_key → Enter
take_snapshot → 获取搜索结果
```

#### 6. 浏览推荐 Feed
```
navigate_page → url: https://www.xiaohongshu.com/explore
take_snapshot → 获取首页内容卡片
evaluate_script → window.scrollBy(0, 800) // 加载更多
```

#### 7. 查看帖子详情
```
// 从搜索/feed结果中找到帖子链接
click → 点击帖子卡片
take_snapshot → 获取标题、正文、点赞数等
```

#### 8. 点赞
```
take_snapshot → 找到点赞按钮（心形图标）→ click
```

#### 9. 收藏
```
take_snapshot → 找到收藏按钮（星形图标）→ click
```

#### 10. 评论
```
take_snapshot → 找到评论输入框 → fill(评论内容)
take_snapshot → 找到发送按钮 → click
```

#### 11. 回复评论
```
take_snapshot → 找到目标评论 → click 回复按钮
fill → 输入回复内容
click → 发送
```

#### 12. 查看用户主页
```
// 从帖子中找到作者链接
click → 点击作者名称
take_snapshot → 获取用户信息和作品列表
```

#### 13. 发布视频
```
navigate_page → url: https://creator.xiaohongshu.com/publish/publish
// 点击"上传视频"
upload_file → 上传视频文件
// 等待视频处理 → 填写标题和描述 → 发布
```

---

## 三、登录流程

当检测到未登录状态时，引导用户登录：

> 需要登录小红书，请选择登录方式：
> 1. **扫码登录** — 打开小红书登录页，展示二维码，用手机APP扫码（推荐）
> 2. **手机号登录** — 输入手机号和验证码

### 方式一：扫码登录

1. 导航到小红书首页
2. 点击登录按钮，弹出登录窗口
3. 截图展示二维码给用户
4. 用户扫码后，刷新页面确认登录状态
5. 确认侧边栏出现"我"菜单项

### 方式二：手机号登录

1. 导航到登录页
2. 点击手机号登录标签
3. 填入手机号，获取验证码
4. 询问用户输入验证码
5. 填入验证码并点击登录
6. 确认登录成功

**登录持久化**：Chrome 使用 symlinked 用户配置目录，登录状态在 Chrome 重启后保持。

---

## 四、安装设置（Mac 环境）

### 必需

- **Google Chrome** — [下载](https://www.google.com/chrome/)
- **Chrome DevTools MCP** — Claude Code 环境中已集成

### 推荐

- **ImageMagick**（封面生成）：`brew install imagemagick`
- **或 Pillow**（封面生成后备）：`pip install Pillow`
- **中文字体**：Mac 系统自带 PingFang/STHeiti，推荐额外安装[阿里巴巴普惠体](https://www.alibabafonts.com/)

### 环境检查

```bash
bash {baseDir}/check_env.sh
```

---

## 五、响应处理

Chrome DevTools 操作后：
- **成功**：通过 `take_snapshot` 或 `take_screenshot` 确认页面状态
- **登录过期**：检测到登录页面时，重新走登录流程
- **元素未找到**：用 `take_snapshot` 获取最新页面结构
- **页面加载慢**：等待 3-5 秒后重试

## 六、注意事项

1. 标题不超过 **20 字**，正文不超过 **500 字**（文字配图模式）
2. 小红书**不支持多设备同时登录**
3. 操作间隔建议 > 3 秒，避免触发反爬
4. 每个关键步骤都应 `take_screenshot` 确认状态
5. 发布成功的判断标准：URL 包含 `published=true`（平台不显示"发布成功"文字）

## 七、故障排查

```bash
# Chrome 调试端口是否就绪
curl -s http://127.0.0.1:9222/json/version

# 重新启动 Chrome 调试模式
bash {baseDir}/scripts/ensure-chrome-debug.sh

# 检查环境
bash {baseDir}/check_env.sh
```

常见问题：
- **Chrome 无法启动调试模式**：确保没有其他 Chrome 实例占用，脚本会自动 kill 现有进程
- **登录状态丢失**：重新执行 `ensure-chrome-debug.sh`，它会复用原有 Chrome 配置
- **封面生成失败**：检查 ImageMagick 或 Pillow 是否安装，检查中文字体是否可用
