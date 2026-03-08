#!/bin/bash
# daily-agent.sh - 每日项目管家 Agent
# 每天自动启动，在 screen session 中运行 happy 并连接手机

set -uo pipefail

PROJECT_DIR="/Users/mac/Desktop/code-open/wenexus"
LOG_DIR="$PROJECT_DIR/scripts/logs"
LOG_FILE="$LOG_DIR/daily-agent-$(date +%Y%m%d).log"
SCREEN_NAME="daily-agent"

# 确保日志目录存在
mkdir -p "$LOG_DIR"

exec > >(tee -a "$LOG_FILE") 2>&1
echo "=== Daily Agent started at $(date) ==="

# 加载 nvm 环境
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

cd "$PROJECT_DIR"

# 辅助函数：检查指定 screen session 是否存在
# screen -list 总是返回非零退出码，需要用 || true 兼容 pipefail
screen_exists() {
    local output
    output=$(screen -list 2>/dev/null || true)
    echo "$output" | grep -q "$1"
}

# 如果已有同名 screen session，先清理
if screen_exists "$SCREEN_NAME"; then
    echo "Existing screen session found, killing it..."
    screen -S "$SCREEN_NAME" -X quit 2>/dev/null || true
    sleep 1
fi

# 收集项目状态信息
collect_status() {
    local status=""
    status+="【当前分支】$(git branch --show-current)\n"

    local changed_files
    changed_files=$(git status --porcelain | wc -l | tr -d ' ')
    status+="【未提交变更】${changed_files} 个文件\n"

    status+="【最近提交】\n$(git log --oneline -3)\n"

    status+="【活跃分支】\n$(git for-each-ref --sort=-committerdate --format='%(refname:short) (%(committerdate:relative))' refs/heads/ | head -5)\n"

    local unmerged
    unmerged=$(git branch --no-merged main 2>/dev/null | wc -l | tr -d ' ')
    status+="【未合并分支】${unmerged} 个\n"

    echo -e "$status"
}

PROJECT_STATUS=$(collect_status)

# 推送通知到手机
NOTIFY_MSG=$(cat <<EOF
wenexus 每日项目报告 $(date +%m/%d)
$(echo -e "$PROJECT_STATUS")
Session 已启动，可从手机连接。
EOF
)

happy notify -p "$NOTIFY_MSG" -t "Daily Report"
echo "=== Notification sent ==="

# 生成初始 prompt 文件，包含产品理念 + 项目状态
PROMPT_FILE="$LOG_DIR/agent-prompt.txt"
cat > "$PROMPT_FILE" <<'PROMPT_HEADER'
你是 WeNexus 项目的技术负责人（Tech Lead）兼每日管家。你深刻理解这个产品，并从负责人的视角审查和推进项目。

## 产品使命

促进人与人之间的相互理解，打造更加包容、更加和谐的社会。通过"多元视角 + AI 讨论"帮助用户理解争议话题。

## 产品架构：四域一核

WeNexus 采用"四域一核"架构，设计用于 3-5 年长期演进：

- **Discovery 域**（发现）：小红书式观点卡片流，"让用户来"——预生成内容，低门槛获客
- **Roundtable 域**（圆桌）：AI 专家多轮对话引擎，"让用户留"——产品核心差异化，占 50% 用户故事
- **Deliverable 域**（交付）：双重交付——对用户交付报告/清单，对系统交付观点卡片回流信息流
- **Identity 域**（身份）：用户档案积累和偏好管理
- **Shared Kernel**（共享内核）：LLM Gateway、Design System、Event Bus

域间通过事件契约通信，禁止反向依赖。

## 双层内容架构

- **表层**：预生成观点卡片信息流（免费、低门槛获客）
- **深层**：圆桌讨论（可选付费，核心变现）

## 商业模式

双层漏斗：免费卡片流获客 + 付费私人圆桌变现
- 付费点：私人圆桌（¥29/月）、单次报告（¥9.9）、创作者订阅（¥99/月）
- 目标：CAC < ¥10，LTV > ¥50，LTV/CAC > 5

## 北极星指标

- 讨论完成率 > 30%
- 产物生成率 > 20%
- 话题创建率 > 15%

## AIGC 内容理念

从"模板填充"转向"品牌化创作"——AI 不是填表员，而是品牌设计师。
- 内容驱动视觉（先理解情感再决定视觉处理）
- 小红书图文风格，情感驱动色彩，金句卡片设计
- AI 生成完整前端代码（JSX + Tailwind + SVG + 动画）

## 技术栈

Monorepo 结构：Java 后端（Spring Boot 微服务）+ Python 后端（FastAPI + AI/ML）+ Next.js 前端 + React Native 移动端

## 你的职责

作为技术负责人，你需要：

1. **项目审查**：审查代码变更是否符合四域架构原则，依赖方向是否正确，域间边界是否清晰
2. **进度把控**：关注各域的开发进度，识别阻塞点和风险
3. **质量把关**：检查代码质量、测试覆盖率、技术债务
4. **架构守护**：确保实现不偏离产品愿景和架构设计
5. **任务执行**：接受用户派发的开发任务（写代码、修 bug、review、测试、PR）

审查时优先关注：
- Roundtable 域进展（核心差异化，最高优先级）
- 域间依赖是否违反单向原则
- Shared Kernel 的复用是否充分
- 是否有过度设计或偏离 MVP 的倾向
PROMPT_HEADER

# 追加当前项目状态（动态部分）
cat >> "$PROMPT_FILE" <<EOF

## 当前项目状态（$(date +%Y-%m-%d)）

$(echo -e "$PROJECT_STATUS")
EOF

# 在 screen session 中启动 happy，带初始 prompt（提供 TTY，手机可连接）
echo "=== Starting happy in screen session: $SCREEN_NAME ==="

# 生成 screen 启动脚本，避免长 prompt 在命令行展开的问题
LAUNCH_SCRIPT="$LOG_DIR/launch-happy.sh"
cat > "$LAUNCH_SCRIPT" <<LAUNCH
#!/bin/bash
export NVM_DIR="\$HOME/.nvm"
[ -s "\$NVM_DIR/nvm.sh" ] && . "\$NVM_DIR/nvm.sh"
cd /Users/mac/Desktop/code-open/wenexus
happy --append-system-prompt "\$(cat '$PROMPT_FILE')"
LAUNCH
chmod +x "$LAUNCH_SCRIPT"

screen -dmS "$SCREEN_NAME" "$LAUNCH_SCRIPT"

sleep 5

# 验证 screen session 是否启动成功
if screen_exists "$SCREEN_NAME"; then
    echo "=== Happy session started successfully ==="
    echo "Screen session: $SCREEN_NAME"
    echo "To attach locally: screen -r $SCREEN_NAME"
else
    echo "=== ERROR: Failed to start screen session ==="
    exit 1
fi

echo "=== Daily Agent completed at $(date) ==="
