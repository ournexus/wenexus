# WeNexus AIGC 架构愿景：面向 AGI 时代的内容生成系统

> 版本: v1.1
> 更新时间: 2026-03-08
> 性质: 技术愿景文档，面向未来 3-5 年

---

## 一、核心哲学

### 1.1 从"模板填充"到"品牌化创作"

```
传统思路                              AGI 时代思路
──────────                            ──────────────

AI 是"填表员"                         AI 是"品牌设计师"
   │                                      │
   ▼                                      ▼
固定模板 + 数据填充                    设计语言 + 自由创作
   │                                      │
   ▼                                      ▼
输出千篇一律                           输出独特且一致
```

**核心转变**：

- ❌ 给 AI 一堆模板，让它选择和填充
- ✅ 给 AI 一套设计语言，让它自由创作

### 1.2 设计语言 vs 组件库

| 维度 | 组件库思维 | 设计语言思维 |
|------|-----------|-------------|
| 约束方式 | "你只能用这些组件" | "这是我们的视觉语言和品味" |
| AI 角色 | 选择器、填充器 | 创作者、艺术家 |
| 输出上限 | 受限于预设组件 | 受限于 AI 能力 |
| 扩展性 | 需要人工添加组件 | AI 自动探索新可能 |

---

## 二、架构全景

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│                         WeNexus AIGC 生成架构                                    │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         输入层 (Input Layer)                             │   │
│  │                                                                         │   │
│  │   话题内容        专家观点        用户偏好        情感基调               │   │
│  │      │              │              │              │                     │   │
│  └──────┼──────────────┼──────────────┼──────────────┼─────────────────────┘   │
│         │              │              │              │                         │
│         ▼              ▼              ▼              ▼                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      语义理解层 (Semantic Layer)                         │   │
│  │                                                                         │   │
│  │   • 提取核心观点和金句                                                   │   │
│  │   • 识别情感张力和冲突点                                                 │   │
│  │   • 理解叙事结构和节奏                                                   │   │
│  │   • 映射内容到视觉意图                                                   │   │
│  │                                                                         │   │
│  └──────────────────────────────────┬──────────────────────────────────────┘   │
│                                     │                                          │
│                                     ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      创意生成层 (Creative Layer)                         │   │
│  │                                                                         │   │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │   │
│  │   │  布局构思   │  │  视觉风格   │  │  动态编排   │  │  情感渲染   │   │   │
│  │   │             │  │             │  │             │  │             │   │   │
│  │   │ • 页面结构  │  │ • 色彩情绪  │  │ • 动画节奏  │  │ • 氛围营造  │   │   │
│  │   │ • 信息层次  │  │ • 排版张力  │  │ • 转场设计  │  │ • 视觉隐喻  │   │   │
│  │   │ • 视觉重心  │  │ • 图形语言  │  │ • 强调时机  │  │ • 情绪曲线  │   │   │
│  │   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │   │
│  │                                                                         │   │
│  └──────────────────────────────────┬──────────────────────────────────────┘   │
│                                     │                                          │
│                                     ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      代码生成层 (Generation Layer)                       │   │
│  │                                                                         │   │
│  │   AI 直接生成完整的前端代码：                                             │   │
│  │                                                                         │   │
│  │   • React/JSX 组件结构                                                   │   │
│  │   • Tailwind CSS 样式                                                    │   │
│  │   • SVG 图形和插画                                                       │   │
│  │   • CSS 动画定义                                                         │   │
│  │   • 渐变和背景合成                                                       │   │
│  │   • 数据可视化图表                                                       │   │
│  │                                                                         │   │
│  └──────────────────────────────────┬──────────────────────────────────────┘   │
│                                     │                                          │
│                                     ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                       渲染层 (Rendering Layer)                           │   │
│  │                                                                         │   │
│  │   前端直接渲染 AI 生成的代码                                              │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 三、AI 的创造力边界

### 3.1 AI 可以创造什么？

AI 不仅是编排者，更是创作者。在设计语言的指导下，AI 可以：

#### 1. 生成完整的页面布局

```jsx
// AI 根据内容自主决定布局结构
<div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
  <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20" />
  <div className="relative z-10 flex flex-col items-center justify-center p-8">
    {/* AI 决定的创意布局 */}
  </div>
</div>
```

#### 2. 生成 SVG 图形和插画

```jsx
// AI 生成的概念性插画
<svg viewBox="0 0 400 300" className="w-full">
  {/* 抽象的"对立与融合"视觉隐喻 */}
  <defs>
    <linearGradient id="tension" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stopColor="#ef4444" />
      <stop offset="50%" stopColor="#8b5cf6" />
      <stop offset="100%" stopColor="#22c55e" />
    </linearGradient>
  </defs>

  {/* 两个对立的圆形，中间产生张力 */}
  <circle cx="100" cy="150" r="60" fill="#ef4444" opacity="0.8">
    <animate attributeName="cx" values="100;120;100" dur="3s" repeatCount="indefinite" />
  </circle>
  <circle cx="300" cy="150" r="60" fill="#22c55e" opacity="0.8">
    <animate attributeName="cx" values="300;280;300" dur="3s" repeatCount="indefinite" />
  </circle>

  {/* 中间的融合区域 */}
  <ellipse cx="200" cy="150" rx="40" ry="60" fill="url(#tension)" opacity="0.6" />
</svg>
```

#### 3. 生成动态背景和氛围

```jsx
// AI 根据内容情感生成背景
<div className="relative overflow-hidden">
  {/* 动态渐变背景 */}
  <div className="absolute inset-0 bg-gradient-to-br from-red-500/20 via-transparent to-green-500/20" />

  {/* 浮动的装饰元素 */}
  <div className="absolute top-10 left-10 w-32 h-32 bg-red-500/10 rounded-full blur-3xl animate-pulse" />
  <div className="absolute bottom-10 right-10 w-40 h-40 bg-green-500/10 rounded-full blur-3xl animate-pulse delay-1000" />

  {/* 网格纹理 */}
  <div className="absolute inset-0 opacity-5">
    <svg width="100%" height="100%">
      <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
        <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="1"/>
      </pattern>
      <rect width="100%" height="100%" fill="url(#grid)" />
    </svg>
  </div>
</div>
```

#### 4. 生成数据可视化

```jsx
// AI 根据数据自动生成可视化
<svg viewBox="0 0 300 200" className="w-full">
  {/* 对比柱状图 */}
  <g transform="translate(50, 20)">
    {/* "反对" 数据 */}
    <rect x="0" y="60" width="80" height="120" fill="#ef4444" rx="4">
      <animate attributeName="height" from="0" to="120" dur="0.8s" fill="freeze" />
      <animate attributeName="y" from="180" to="60" dur="0.8s" fill="freeze" />
    </rect>
    <text x="40" y="40" textAnchor="middle" className="fill-white text-lg font-bold">67%</text>
    <text x="40" y="195" textAnchor="middle" className="fill-gray-400 text-xs">反对派</text>

    {/* "支持" 数据 */}
    <rect x="120" y="120" width="80" height="60" fill="#22c55e" rx="4">
      <animate attributeName="height" from="0" to="60" dur="0.8s" fill="freeze" />
      <animate attributeName="y" from="180" to="120" dur="0.8s" fill="freeze" />
    </rect>
    <text x="160" y="105" textAnchor="middle" className="fill-white text-lg font-bold">33%</text>
    <text x="160" y="195" textAnchor="middle" className="fill-gray-400 text-xs">支持派</text>
  </g>
</svg>
```

#### 5. 生成创意排版

```jsx
// AI 生成有张力的排版
<div className="relative">
  {/* 大标题，带有视觉冲击 */}
  <h1 className="text-6xl font-black tracking-tighter">
    <span className="bg-clip-text text-transparent bg-gradient-to-r from-red-500 to-orange-500">
      付费内推
    </span>
    <br />
    <span className="text-white/90">是新时代的</span>
    <br />
    <span className="relative inline-block">
      <span className="relative z-10 text-white">买官卖爵</span>
      <span className="absolute inset-0 bg-red-500/30 -skew-x-12 transform" />
    </span>
    <span className="text-white/90">？</span>
  </h1>

  {/* 署名 */}
  <div className="mt-8 flex items-center gap-3">
    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center">
      🎭
    </div>
    <div>
      <div className="text-white font-medium">鲁迅</div>
      <div className="text-gray-400 text-sm">社会手术刀</div>
    </div>
  </div>
</div>
```

#### 6. 生成情感化动画

```jsx
// AI 根据内容情感设计动画
<style jsx>{`
  @keyframes tension-pulse {
    0%, 100% { transform: scale(1); opacity: 0.8; }
    50% { transform: scale(1.05); opacity: 1; }
  }

  @keyframes float-in {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @keyframes shake-subtle {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-2px); }
    75% { transform: translateX(2px); }
  }

  .animate-tension { animation: tension-pulse 2s ease-in-out infinite; }
  .animate-float-in { animation: float-in 0.6s ease-out forwards; }
  .animate-shake { animation: shake-subtle 0.5s ease-in-out; }
`}</style>
```

---

### 3.2 设计语言作为"品味指南"

AI 不是无约束创作，而是在品牌设计语言的指导下创作。

#### 设计语言文档结构

```markdown
# WeNexus 设计语言 v1.0

## 1. 品牌性格
- 理性但不冷漠
- 多元但不混乱
- 深度但不晦涩
- 有态度但不偏激

## 2. 视觉原则

### 色彩情感映射
| 情感 | 主色 | 用法 |
|------|------|------|
| 批判/质疑 | 红色系 | 观点卡片边框、强调文字 |
| 支持/认同 | 绿色系 | 共识区域、正面观点 |
| 中立/分析 | 蓝色/紫色系 | 数据、求真者内容 |
| 冲突/张力 | 红绿渐变 | VS 对比、辩论区域 |

### 排版张力
- 标题：大胆、有冲击力、可以破格
- 金句：突出、可以使用装饰性背景
- 正文：克制、易读、留白充足

### 动效原则
- 入场：轻盈、自然，不要太花哨
- 强调：微妙的脉动或位移
- 冲突：可以有轻微的抖动或对抗感

## 3. 禁忌
- 不要使用过于卡通的风格
- 不要使用过于严肃/政府公文的风格
- 不要使用过多颜色（一页不超过3种主色）
- 不要使用低质量的图片或图标
```

---

## 四、技术实现路径

### 4.1 Prompt Engineering：教 AI 成为设计师

```markdown
# System Prompt

你是 WeNexus 的视觉设计 AI。你的任务是将专家讨论内容转化为精美的小红书风格卡片。

## 你的能力

你可以生成完整的 React 组件代码，包括：
- JSX 结构
- Tailwind CSS 样式
- SVG 图形（用于插画、图标、数据可视化）
- CSS 动画（用于强调和情感表达）

## 设计语言

[嵌入设计语言文档]

## 创作原则

1. **内容驱动视觉**：先理解内容的情感和结构，再决定视觉处理
2. **张力与平衡**：观点冲突要有视觉张力，但整体要和谐
3. **留白即呼吸**：不要填满每一寸空间
4. **动效即情感**：动画要服务于情感表达，不是炫技

## 输出格式

直接输出可执行的 React 组件代码。每个 Slide 是一个独立的组件。

## 示例

[提供 3-5 个高质量示例]
```

### 4.2 渲染架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   AI 输出                     解析层                     渲染层              │
│                                                                             │
│   ┌───────────┐           ┌───────────┐           ┌───────────┐           │
│   │           │           │           │           │           │           │
│   │  React    │    →      │   AST     │    →      │  React    │           │
│   │  JSX      │           │  Parser   │           │  Runtime  │           │
│   │  Code     │           │           │           │           │           │
│   │           │           │           │           │           │           │
│   └───────────┘           └───────────┘           └───────────┘           │
│                                                                             │
│   包含：                    功能：                    功能：                 │
│   - 组件结构                - 解析 JSX               - 直接渲染              │
│   - Tailwind 类             - 提取样式               - 支持所有 CSS          │
│   - SVG 代码                - 处理 SVG               - 支持 SVG              │
│   - CSS 动画                - 处理动画               - 支持动画              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 流式生成体验

> **实现难点**：增量 JSX 解析（在 AI 流式输出中实时解析不完整的 JSX）是一个工程难题。
> 需要自研或引入支持增量解析的 JSX 编译器，候选方案包括基于 SWC/Babel 的自定义 parser
> 或按 Slide 分隔符（如 `{/* Slide N */}`）进行文本级切割后整段编译。

```jsx
// 概念设计：用户看到的是逐步生成的精美卡片
// 注意：slideParser 和 compileSlideJSX 需要自研实现
function StreamingSlides({ aiStream }) {
  const [slides, setSlides] = useState([]);
  const [currentSlide, setCurrentSlide] = useState(null);

  useEffect(() => {
    // 按 Slide 分隔符切割流式输出，每完成一个 Slide 整段编译
    // 方案 A：基于文本分隔符切割（简单，推荐基线阶段使用）
    // 方案 B：基于 AST 的增量解析（复杂，后续优化方向）
    const buffer = new SlideStreamBuffer(aiStream, {
      separator: /\{\/\*\s*Slide\s+\d+/,
    });

    buffer.onSlideComplete((slideCode) => {
      // 使用 SWC 或 Babel 编译完整的 Slide JSX
      const CompiledSlide = compileSlideJSX(slideCode);
      setSlides(prev => [...prev, CompiledSlide]);
    });

    buffer.onProgress((partialCode) => {
      setCurrentSlide(partialCode);
    });
  }, [aiStream]);

  return (
    <div className="snap-y snap-mandatory overflow-y-auto h-screen">
      {slides.map((Slide, i) => (
        <div key={i} className="snap-start h-screen">
          <Slide />
        </div>
      ))}

      {currentSlide && (
        <div className="snap-start h-screen opacity-50">
          <GeneratingPreview code={currentSlide} />
        </div>
      )}
    </div>
  );
}
```

---

## 五、示例：完整的 AI 输出

以下是 AI 针对"付费内推"话题可能生成的完整输出：

```jsx
{/* Slide 1: 封面 - 视觉冲击 */}
<div className="min-h-screen bg-gradient-to-br from-slate-900 via-red-950 to-slate-900 flex flex-col justify-center p-8 relative overflow-hidden">
  {/* 动态背景 */}
  <div className="absolute inset-0">
    <div className="absolute top-1/4 -left-20 w-80 h-80 bg-red-500/20 rounded-full blur-3xl animate-pulse" />
    <div className="absolute bottom-1/4 -right-20 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl animate-pulse delay-700" />
  </div>

  {/* 主标题 */}
  <div className="relative z-10">
    <div className="text-red-400/60 text-sm font-medium tracking-widest mb-4">争议话题</div>
    <h1 className="text-5xl font-black text-white leading-tight mb-6">
      付费内推
      <br />
      <span className="relative inline-block mt-2">
        <span className="relative z-10">是割韭菜吗？</span>
        <span className="absolute bottom-2 left-0 right-0 h-4 bg-red-500/30 -skew-x-6" />
      </span>
    </h1>

    {/* 专家阵容预览 */}
    <div className="flex items-center gap-2 mt-8">
      <div className="flex -space-x-3">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-700 to-gray-800 border-2 border-slate-900 flex items-center justify-center text-lg">🎭</div>
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-700 to-gray-800 border-2 border-slate-900 flex items-center justify-center text-lg">💼</div>
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-700 to-gray-800 border-2 border-slate-900 flex items-center justify-center text-lg">👵</div>
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-700 to-gray-800 border-2 border-slate-900 flex items-center justify-center text-lg">🔬</div>
      </div>
      <span className="text-gray-400 text-sm">4 位专家激辩中</span>
    </div>
  </div>

  {/* 下滑提示 */}
  <div className="absolute bottom-8 left-1/2 -translate-x-1/2 text-gray-500 text-sm animate-bounce">
    ↓ 滑动查看
  </div>
</div>

{/* Slide 2: 核心冲突 - VS 对比 */}
<div className="min-h-screen bg-slate-900 p-6 flex flex-col justify-center relative">
  {/* 背景分割 */}
  <div className="absolute inset-0 flex">
    <div className="w-1/2 bg-gradient-to-br from-red-950/50 to-transparent" />
    <div className="w-1/2 bg-gradient-to-bl from-green-950/50 to-transparent" />
  </div>

  <div className="relative z-10">
    <h2 className="text-center text-gray-400 text-sm font-medium tracking-widest mb-8">观点交锋</h2>

    <div className="flex gap-4">
      {/* 反对方 */}
      <div className="flex-1 bg-red-950/30 rounded-2xl p-5 border border-red-800/30">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-full bg-red-900/50 flex items-center justify-center">🎭</div>
          <div>
            <div className="text-white text-sm font-medium">鲁迅</div>
            <div className="text-red-400 text-xs">反对</div>
          </div>
        </div>
        <p className="text-gray-300 text-sm leading-relaxed">
          "所谓付费内推，不过是<span className="text-red-400 font-medium">新时代的买官卖爵</span>，本质是用金钱购买本应公平竞争的机会。"
        </p>
      </div>

      {/* VS */}
      <div className="flex items-center">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-red-500 to-green-500 flex items-center justify-center text-white font-bold text-sm">
          VS
        </div>
      </div>

      {/* 支持方 */}
      <div className="flex-1 bg-green-950/30 rounded-2xl p-5 border border-green-800/30">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-full bg-green-900/50 flex items-center justify-center">💼</div>
          <div>
            <div className="text-white text-sm font-medium">企业家</div>
            <div className="text-green-400 text-xs">支持</div>
          </div>
        </div>
        <p className="text-gray-300 text-sm leading-relaxed">
          "公平竞争从来不存在。内推只是<span className="text-green-400 font-medium">把隐性成本显性化</span>了，这是市场经济的正常现象。"
        </p>
      </div>
    </div>
  </div>
</div>

{/* Slide 3: 数据洞察 */}
<div className="min-h-screen bg-slate-900 p-6 flex flex-col justify-center">
  <div className="flex items-center gap-2 mb-6">
    <div className="w-8 h-8 rounded-full bg-blue-900/50 flex items-center justify-center">🔬</div>
    <div>
      <div className="text-white text-sm font-medium">求真者</div>
      <div className="text-blue-400 text-xs">事实核查</div>
    </div>
  </div>

  <h2 className="text-xl font-bold text-white mb-6">数据告诉我们什么？</h2>

  {/* AI 生成的 SVG 数据可视化 */}
  <svg viewBox="0 0 320 180" className="w-full mb-6">
    {/* 背景 */}
    <rect x="0" y="0" width="320" height="180" fill="transparent" />

    {/* 数据柱 */}
    <g transform="translate(40, 20)">
      {/* 费用柱 */}
      <rect x="20" y="40" width="60" height="100" fill="url(#redGradient)" rx="4">
        <animate attributeName="height" from="0" to="100" dur="0.6s" fill="freeze" />
        <animate attributeName="y" from="140" to="40" dur="0.6s" fill="freeze" />
      </rect>
      <text x="50" y="30" textAnchor="middle" fill="#f87171" fontSize="20" fontWeight="bold">¥3万</text>
      <text x="50" y="160" textAnchor="middle" fill="#9ca3af" fontSize="10">平均费用</text>

      {/* 投诉率柱 */}
      <rect x="140" y="60" width="60" height="80" fill="url(#orangeGradient)" rx="4">
        <animate attributeName="height" from="0" to="80" dur="0.6s" fill="freeze" delay="0.2s" />
        <animate attributeName="y" from="140" to="60" dur="0.6s" fill="freeze" delay="0.2s" />
      </rect>
      <text x="170" y="50" textAnchor="middle" fill="#fb923c" fontSize="20" fontWeight="bold">72%</text>
      <text x="170" y="160" textAnchor="middle" fill="#9ca3af" fontSize="10">投诉率</text>
    </g>

    {/* 渐变定义 */}
    <defs>
      <linearGradient id="redGradient" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#ef4444" />
        <stop offset="100%" stopColor="#dc2626" />
      </linearGradient>
      <linearGradient id="orangeGradient" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#f97316" />
        <stop offset="100%" stopColor="#ea580c" />
      </linearGradient>
    </defs>
  </svg>

  <div className="bg-blue-950/30 rounded-xl p-4 border border-blue-800/30">
    <p className="text-gray-300 text-sm leading-relaxed">
      据黑猫投诉平台数据，付费内推相关投诉中，<span className="text-blue-400 font-medium">72% 反映未能成功入职</span>，平均损失约 3 万元。
    </p>
    <div className="text-gray-500 text-xs mt-2">来源：黑猫投诉 2024 年数据</div>
  </div>
</div>

{/* Slide 4: 情感共鸣 */}
<div className="min-h-screen bg-slate-900 p-6 flex flex-col justify-center">
  <div className="bg-gradient-to-br from-amber-950/40 to-orange-950/20 rounded-2xl p-6 border border-amber-800/20">
    <div className="flex items-center gap-3 mb-4">
      <div className="w-12 h-12 rounded-full bg-amber-900/50 flex items-center justify-center text-2xl">👵</div>
      <div>
        <div className="text-white font-medium">王阿姨</div>
        <div className="text-amber-400 text-xs">社区情报中心</div>
      </div>
    </div>

    <blockquote className="text-lg text-white leading-relaxed mb-4">
      "我家孩子攒了一年工资才凑够这 3 万块，结果还被骗了！"
    </blockquote>

    <div className="flex items-center gap-4 text-sm">
      <div className="flex items-center gap-1 text-red-400">
        <span>😢</span>
        <span>2.3k 共鸣</span>
      </div>
      <div className="flex items-center gap-1 text-gray-400">
        <span>💬</span>
        <span>查看回应</span>
      </div>
    </div>
  </div>

  {/* 关联观点 */}
  <div className="mt-4 bg-slate-800/50 rounded-xl p-4">
    <div className="text-gray-400 text-xs mb-2">💼 企业家回应</div>
    <p className="text-gray-300 text-sm">
      "你说得轻巧！那些没钱的孩子怎么办？这不就是在<span className="text-amber-400">制造新的不公平</span>吗？"
    </p>
  </div>
</div>

{/* Slide 5: 理解地图 */}
<div className="min-h-screen bg-slate-900 p-6 flex flex-col justify-center">
  <h2 className="text-xl font-bold text-white mb-6">理解地图</h2>

  <div className="space-y-4">
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-400">事实共识度</span>
        <span className="text-emerald-400">80%</span>
      </div>
      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
        <div className="h-full w-4/5 bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-full" />
      </div>
    </div>

    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-400">立场理解度</span>
        <span className="text-blue-400">65%</span>
      </div>
      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
        <div className="h-full w-[65%] bg-gradient-to-r from-blue-500 to-blue-400 rounded-full" />
      </div>
    </div>

    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-400">分歧根源</span>
        <span className="text-amber-400">40%</span>
      </div>
      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
        <div className="h-full w-2/5 bg-gradient-to-r from-amber-500 to-amber-400 rounded-full" />
      </div>
    </div>
  </div>

  <div className="mt-8 bg-slate-800/50 rounded-xl p-4">
    <div className="text-purple-400 text-sm font-medium mb-2">💡 核心分歧</div>
    <p className="text-gray-300 text-sm leading-relaxed">
      争论的本质不是"内推好不好"，而是<span className="text-white font-medium">"机会应该如何分配"</span>——是承认现实的不公平，还是追求理想的公平？
    </p>
  </div>

  <button className="mt-6 w-full py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-medium rounded-xl">
    查看完整讨论
  </button>
</div>
```

---

## 六、进化路径

### 阶段 1：基础创作能力（当前）

```
AI 能力：
├── 生成结构化 JSX
├── 使用 Tailwind 进行样式控制
├── 生成简单 SVG 图形
└── 基础动画效果

约束：
├── 需要详细的 Prompt 指导
├── 风格一致性需要人工调整
└── 复杂布局可能出错
```

### 阶段 2：风格化创作（6-12个月）

```
AI 能力：
├── 理解并执行设计语言
├── 生成复杂 SVG 插画
├── 自主决定布局和动效
└── 情感到视觉的自动映射

约束：
├── 设计语言文档作为指导
├── 少量示例即可学习风格
└── 需要偶尔人工修正
```

### 阶段 3：AGI 级创作（2-3年）

```
AI 能力：
├── 完全理解品牌调性
├── 生成任何复杂度的视觉
├── 发明新的视觉表达方式
├── 个性化风格适配
└── 多模态生成（图文+音视频）

约束：
├── 仅受品牌价值观约束
├── 人工角色变为"艺术总监"
└── AI 提案，人类审核
```

---

## 七、与竞品的差异化

| 维度 | Canva/美图 | v0.dev | WeNexus |
|------|-----------|--------|---------|
| 定位 | 设计平台（模板 + AI 生成） | 代码生成 | 内容+视觉一体化 |
| AI 角色 | AI 辅助设计（Magic Studio 支持文生图、AI 排版） | 代码生成 | 内容理解 → 视觉创作 |
| 输入 | 用户选模板或描述需求 | 用户描述需求 | 讨论内容自动转视觉 |
| 输出 | 静态图片/视频 | 代码 | 可交互的内容体验 |
| 差异点 | 通用设计工具，不理解内容语义 | 通用代码工具，不理解内容语义 | 深度绑定讨论语义（专家观点、情感张力、共识度） |

---

## 八、关键成功因素

1. **设计语言的深度**：不是简单的颜色/字体规范，而是完整的视觉哲学
2. **示例的质量**：Few-shot learning 依赖高质量示例
3. **反馈循环**：用户反馈 → 优化 Prompt → 更好输出
4. **模型选择**：需要视觉理解能力强的模型（Claude/GPT-4V）

---

## 九、下一步行动

1. **建立设计语言文档**：完整的视觉哲学和规范
2. **创建 10 个黄金示例**：覆盖不同话题和情感
3. **搭建渲染管线**：支持 AI 生成的 JSX 直接渲染
4. **Prompt 迭代**：基于输出质量持续优化

---

## 十、小红书图文视觉特征分析

> 更新时间: 2025-01-28
> 本节基于对小红书爆款图文的深度分析

### 10.1 为什么现有实现像 PPT？

| 维度 | 当前实现 | 小红书图文 |
|------|---------|-----------|
| 色彩 | 单一暗色背景 | 丰富渐变、情感配色 |
| 排版 | 规整、层次分明 | 大胆、打破常规、视觉冲击 |
| 装饰 | 几乎没有 | 表情符号、贴纸、装饰图形 |
| 信息密度 | 高、紧凑 | 低、留白大、一页一观点 |
| 情感表达 | 冷静、理性 | 热烈、有温度、引发共鸣 |
| 互动感 | 无 | 点赞数、评论预览、引导互动 |

### 10.2 小红书图文的核心视觉语言

#### 1. 情感驱动的色彩系统

```
情感基调 → 主色调 → 渐变方向 → 装饰色

争议/冲突  → 红橙系 → 对角渐变 → 黄色点缀
支持/正向  → 绿青系 → 向上渐变 → 金色点缀
理性/分析  → 蓝紫系 → 水平渐变 → 银色点缀
情感/共鸣  → 粉橙系 → 柔和渐变 → 暖白点缀
中立/客观  → 灰蓝系 → 微妙渐变 → 冷白点缀
```

#### 2. 标题的视觉冲击力

小红书标题不是简单的文字，而是**视觉元素**：

```
技法1: 大小对比
┌────────────────────────┐
│  付费内推              │  ← 超大字
│  真的是                │  ← 中等字
│  割韭菜吗？            │  ← 超大字 + 高亮
└────────────────────────┘

技法2: 颜色分层
┌────────────────────────┐
│  这个观点              │  ← 灰色
│  99%的人              │  ← 金色/高亮
│  都理解错了            │  ← 白色
└────────────────────────┘

技法3: 装饰强调
┌────────────────────────┐
│  ══════════════════    │  ← 装饰线
│  🔥 专家激辩           │  ← 表情符号 + 标签
│  ══════════════════    │  ← 装饰线
└────────────────────────┘
```

#### 3. 金句卡片设计

金句是小红书的灵魂，需要特殊的视觉处理：

```
样式1: 引号突出
┌────────────────────────┐
│  "                     │ ← 超大装饰引号
│    所谓内推，不过是     │
│    新时代的买官卖爵     │
│                    "   │
│              —— 鲁迅   │
└────────────────────────┘

样式2: 背景色块
┌────────────────────────┐
│ ┌──────────────────┐   │
│ │  ████ 核心观点 ████ │ │ ← 色块背景
│ │  这句话直接戳中痛点  │ │
│ └──────────────────┘   │
└────────────────────────┘

样式3: 手写风批注
┌────────────────────────┐
│  付费3万，啥也没得到    │
│       ↑                │
│    「划重点」          │ ← 批注风格
└────────────────────────┘
```

#### 4. 数据可视化的小红书化

不是 Excel 图表，而是**情感化的数据展示**：

```
样式1: 大数字冲击
┌────────────────────────┐
│         72%            │ ← 超大数字
│      ──────            │
│    投诉率竟然这么高！   │ ← 情感化解读
└────────────────────────┘

样式2: 对比条
┌────────────────────────┐
│  支持 ████████░░ 67%   │
│  反对 ███░░░░░░░ 33%   │
│        ↑               │
│    差距居然这么大      │
└────────────────────────┘

样式3: 表情符号计数
┌────────────────────────┐
│  😢😢😢😢😢😢😢░░░       │
│  7/10 的人表示受过骗   │
└────────────────────────┘
```

#### 5. 专家身份的人格化

不是冷冰冰的头像+名字，而是**有温度的人设**：

```
┌────────────────────────┐
│  ┌────┐                │
│  │ 🎭 │  鲁迅           │ ← 个性化头像
│  └────┘  @社会手术刀    │ ← 人设标签
│          ──────────    │
│  「这位专家以犀利著称」  │ ← 人设描述
└────────────────────────┘
```

#### 6. 互动元素

制造参与感，而不是单向输出：

```
页面底部互动条
┌────────────────────────┐
│  ❤️ 2.3k  💬 328  ⭐ 收藏 │
│  ──────────────────────│
│  「你怎么看？评论区见」  │ ← 引导互动
└────────────────────────┘

投票互动
┌────────────────────────┐
│  你支持哪方观点？       │
│  ┌─────────────────┐   │
│  │ 👍 支持内推 (34%)│   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ 👎 反对内推 (66%)│   │
│  └─────────────────┘   │
└────────────────────────┘
```

### 10.3 组件系统设计原则

基于以上分析，新的组件系统应遵循：

```
┌─────────────────────────────────────────────────────────────┐
│                    WeNexus 组件设计原则                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 情感优先                                                 │
│     └── 每个组件都有情感变体（mood-xxx）                      │
│                                                             │
│  2. 视觉张力                                                 │
│     └── 提供「安全」和「大胆」两套强度选项                    │
│                                                             │
│  3. 装饰丰富                                                 │
│     └── 内置表情符号、装饰线、光效等装饰元素                  │
│                                                             │
│  4. 留白充足                                                 │
│     └── 默认大间距，让内容呼吸                               │
│                                                             │
│  5. 互动暗示                                                 │
│     └── 内置点赞、评论等互动元素样式                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 10.4 新组件系统架构

```
组件层级结构
═══════════════════════════════════════════════════════════════

第一层：页面容器
├── .xhs-page                    # 单页容器（替代 xhs-slide）
├── .xhs-page--cover             # 封面页
├── .xhs-page--content           # 内容页
├── .xhs-page--quote             # 金句页
├── .xhs-page--data              # 数据页
├── .xhs-page--versus            # 对比页
└── .xhs-page--cta               # 行动召唤页

第二层：情感修饰符
├── .mood-conflict               # 冲突/争议（红橙系）
├── .mood-support                # 支持/正向（绿青系）
├── .mood-analytical             # 理性/分析（蓝紫系）
├── .mood-emotional              # 情感/共鸣（粉橙系）
└── .mood-neutral                # 中立/客观（灰蓝系）

第三层：内容组件
├── 标题系统
│   ├── .xhs-title               # 主标题（自动视觉处理）
│   ├── .xhs-title--hero         # 超大封面标题
│   ├── .xhs-title--impact       # 冲击力标题（大小对比）
│   └── .xhs-subtitle            # 副标题
│
├── 金句系统
│   ├── .xhs-quote               # 金句容器
│   ├── .xhs-quote--large        # 大号金句
│   ├── .xhs-quote--annotated    # 带批注金句
│   └── .xhs-quote-author        # 金句作者
│
├── 卡片系统
│   ├── .xhs-card                # 基础卡片
│   ├── .xhs-card--glass         # 毛玻璃卡片
│   ├── .xhs-card--gradient      # 渐变卡片
│   ├── .xhs-card--bordered      # 边框卡片
│   └── .xhs-card--floating      # 浮动卡片（阴影）
│
├── 专家系统
│   ├── .xhs-expert              # 专家信息
│   ├── .xhs-expert--large       # 大号专家卡片
│   ├── .xhs-expert-avatar       # 头像
│   ├── .xhs-expert-name         # 姓名
│   ├── .xhs-expert-tagline      # 人设标签
│   └── .xhs-expert-badge        # 立场徽章（支持/反对）
│
├── 数据展示
│   ├── .xhs-stat                # 统计数字
│   ├── .xhs-stat--huge          # 超大数字
│   ├── .xhs-progress            # 进度条
│   ├── .xhs-progress--versus    # 对比进度条
│   └── .xhs-emoji-meter         # 表情符号计数
│
├── 对比组件
│   ├── .xhs-versus              # VS 对比容器
│   ├── .xhs-versus-side         # 对比单侧
│   ├── .xhs-versus-badge        # VS 徽章
│   └── .xhs-versus--stacked     # 堆叠式对比
│
└── 互动组件
    ├── .xhs-engagement          # 互动条
    ├── .xhs-vote                # 投票组件
    └── .xhs-cta                 # 行动按钮

第四层：装饰与特效
├── .xhs-highlight               # 荧光笔高亮
├── .xhs-underline               # 装饰下划线
├── .xhs-glow                    # 发光效果
├── .xhs-float                   # 浮动动画
├── .xhs-pulse                   # 脉冲动画
└── .xhs-decoration--xxx         # 各类装饰元素
```

### 10.5 Prompt 设计策略

AI 不是简单选择组件，而是**理解内容情感后进行创意组合**：

```markdown
# Prompt 结构

## 第一步：内容分析
AI 首先分析输入内容：
- 核心观点是什么？
- 情感基调是什么？（冲突/支持/理性/情感/中立）
- 有哪些金句值得突出？
- 数据点有哪些？
- 专家立场如何？

## 第二步：叙事结构设计
AI 规划 5 页内容的叙事结构：
- P1: 钩子页 - 用什么方式抓住眼球？
- P2: 核心冲突 - 如何展示观点对立？
- P3: 深度分析 - 用什么方式呈现洞察？
- P4: 情感共鸣 - 哪个专家观点最能引发共鸣？
- P5: 行动引导 - 如何引导用户参与讨论？

## 第三步：视觉创作
基于叙事结构，AI 选择合适的：
- 页面类型（cover/content/quote/data/versus/cta）
- 情感修饰符（mood-xxx）
- 内容组件组合
- 装饰元素

## 输出要求
- 使用语义化类名组合
- 每页内容精炼（<100字）
- 必须有视觉锚点（金句/数据/专家）
- 适当使用表情符号增加趣味
```

---

*这是一份面向未来的愿景文档。核心信念是：AI 的创造力应该被释放，而不是被框架束缚。设计系统是品味的指南，而不是能力的牢笼。*
