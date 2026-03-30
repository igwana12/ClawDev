# 🦞 ClawDev - 让AI为你打工：一只"龙虾"的自我修养

> 从"只会聊天"到"自主执行"——我如何用OpenClaw构建了一个AI软件开发团队

![ClawDev](https://img.shields.io/github/stars/HDAnzz/ClawDev?style=flat&color=ff6b6b)

<!-- TODO: 添加项目截图 -->

## 🦐 前言：当AI不再是"人工智障"

你是否受够了每次让AI写代码，它却只给你一段注释？
你是否梦想过有一个AI团队，24小时为你写代码、审代码、测代码？

今天，我"饲养"了一只特别的龙虾——**ClawDev**，它不再只是聊天，而是真的能干活！

## 🦞 一、什么是ClawDev？

**ClawDev** 是一个基于 OpenClaw ACP 的多智能体软件开发框架。它让AI不再局限于对话窗口，而是通过结构化的阶段流程，真正"自主执行"软件开发任务。

```
用户需求 → 需求分析 → 语言选择 → 编码 → 代码审查 → 测试 → 文档
    ↓         ↓         ↓       ↓        ↓       ↓      ↓
  CEO        CPO       CTO  Programmer Reviewer Tester Programmer
```

每个阶段都有专门的AI角色，它们分工协作，像真实的软件公司一样运作！

## 🦐 二、部署我的"龙虾"

> ⚠️ **前置条件**：先运行 `openclaw` 完成 onboard 配置模型供应商

### 2.1 克隆项目

```bash
git clone https://github.com/HDAnzz/ClawDev.git
cd ClawDev
```

### 2.2 设置 OPENCLAW_CONFIG_HOST

```bash
export OPENCLAW_CONFIG_HOST=~/.openclaw
```

脚本会自动创建 `.env` 文件。

### 2.3 一键部署

```bash
./scripts/deploy.sh
```

脚本会自动完成：
1. 配置 openclaw.json（acp + remote）
2. 安装依赖
3. 创建智能体
4. 启动 Gitea 容器
5. 在 Gitea 创建智能体账户
6. 部署智能体凭证
7. 安装所需技能
8. 配置沙箱

> ⚠️ Gitea 启动后需访问 http://host.docker.internal:3000 完成初始化

### 2.4 运行 ClawDev

```bash
uv run src/main.py "你的任务描述"
```

<!-- TODO: 截图 - 阿里云轻量服务器控制台 -->

### 2.12 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                    ClawDev Framework                    │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   ChatChain │  │ ChatEnv     │  │AgentAdapter │    │
│  │  (编排器)   │  │ (环境管理)  │  │ (适配器)    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
├─────────────────────────────────────────────────────────┤
│                     Phase Engine                         │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │
│  │Demand│ │Coding│ │Review│ │ Test │ │ Docs │       │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘       │
├─────────────────────────────────────────────────────────┤
│                  OpenClaw ACP Protocol                  │
│  ┌─────────────────────────────────────────────────┐    │
│  │ WebSocket → JSON-RPC 2.0 → Agent Session       │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 🦞 三、实战！让龙虾写一个计算器

### 3.1 任务输入

```python
task = "用Python写一个支持加减乘除的计算器GUI程序"
```

### 3.2 阶段执行

<!-- TODO: 截图 - 控制台日志显示各阶段执行 -->

#### 🐢 阶段1：需求分析（CEO ↔ CPO）

```
CEO: "用户需要一个计算器，请分析最佳产品形态"
CPO: "GUI桌面应用最佳，交互最自然<result>GUI Application</result>"
```

#### 🐢 阶段2：编码（CodingInit → CodingImprove）

```
CTO: "创建仓库，邀请Programmer，写初始代码并提交PR"
Programmer: "完成！PR已创建 https://gitea/.../pull/1"
CTO: "<result>Done</result>"
```

#### 🐢 阶段3：代码审查

```
CTO: "添加Reviewer为成员，发送审核请求"
Reviewer: "发现3个问题：1.除零错误 2.未处理负数 3.缺少异常捕获"
CTO: "好的，让Programmer修复"
Programmer: "修复完成，新PR: https://gitea/.../pull/2"
CTO: "代码质量合格，合并PR <result>Done</result>"
```

#### 🐢 阶段4：测试

```
Tester: "运行测试，发现除法测试失败"
Programmer: "修复除法精度问题"
Tester: "全部通过 <result>Done</result>"
```

### 3.3 最终产出

<!-- TODO: 截图 - 计算器运行界面 -->

一只活生生的计算器exe文件！
用户双击打开就能用。

## 🦐 四、技术亮点

### 4.1 对话式协作

不是简单的API调用，而是真正的**对话协作**：
- 每个阶段是两个AI角色的对话
- 用`<result>`标签控制阶段结束
- 支持多轮迭代直到任务完成

### 4.2 Gitea工作流深度集成

<!-- TODO: 截图 - Gitea仓库和PR列表 -->

```bash
# 自动化的代码管理
tea repo create              # 创建仓库
tea repo add-collaborator   # 添加成员
tea pr create               # 创建PR
tea pr merge                # 合并PR
```

### 4.3 可配置的多阶段流程

```json
{
  "phase": "Coding",
  "phaseType": "ComposedPhase",
  "cycleNum": 1,
  "composition": [
    { "phase": "CodingInit", "phaseType": "SimplePhase" },
    { "phase": "CodingImprove", "phaseType": "SimplePhase" }
  ]
}
```

## 🦞 五、真实应用场景

| 场景 | 效果 |
|------|------|
| 快速原型 | 描述需求 → 自动生成可运行程序 |
| 代码审查 | 自动找bug，提改进建议 |
| 文档生成 | 自动生成API文档 |
| 批量处理 | 同时开发多个小工具 |

## 🦐 六、饲养心得

### 6.1 快乐瞬间

<!-- TODO: 截图 - AI自动创建的Gitea仓库、PR记录 -->

- ✅ 第一次看到AI自己创建仓库、提交代码
- ✅ 第一次AI自己code review自己修复
- ✅ 第一次AI生成完整的项目文档

### 6.2 进化方向

- 📌 支持更多代码仓库（GitHub、GitLab）
- 📌 增加插件系统
- 📌 支持更多AI模型

## 🦞 结语

这就是我的"龙虾"——ClawDev。它不只是一段代码，而是一个真正的AI开发团队。

**当你睡觉时，它在写代码。**
**当你吃饭时，它在跑测试。**
**当你上班时，它已经准备好了今天要用的工具。**

这才是AI应该有的样子——不是chatbot，而是workhorse！

---

> 🦞 **队名**：ClawDev Studio  
> 📧 **联系方式**：GitHub @HDAnzz  
> 🔗 **项目地址**：https://github.com/HDAnzz/ClawDev
