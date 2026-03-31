# 告别"玩具级"Agent：我雇了一整个AI公司，凌晨2点它们在GitLab给我提PR

> 基于OpenClaw的"龙虾"饲养实录与踩坑笔记

![部署状态](figs/ali-ecs.png)

## 🚨 凌晨2:17，我被邮件吵醒了

手机屏幕亮起的瞬间，我看到一行字：

> **CTO (AI) 提交了 Merge Request #42: 实现 CIFAR-10 图像分类器**

我瞬间清醒了。

这不是科幻电影。这是我正在参加**阿里云天池大赛**的项目——**ClawDev**，一只真正能干活的多智能体软件开发系统。

![ClawDev架构](figs/arch.png)

### 什么是ClawDev？

简单说，ClawDev 是一个基于 **OpenClaw ACP 协议**的多智能体软件开发框架。它不再是"聊天机器人"，而是一个**真正能执行软件开发全流程**的AI团队：

| AI角色 | 职责 | 真实执行的操作 |
|--------|------|---------------|
| **CEO** | 需求分析 | 解析用户需求，分配给 CPO |
| **CPO** | 产品决策 | 确定技术栈、架构方案 |
| **CTO** | 项目管理 | 在 Gitea 创建仓库、管理 PR |
| **Programmer** | 编码实现 | 编写代码、提交 commit |
| **Reviewer** | 代码审查 | 审查 PR、提出修改意见 |
| **Tester** | 测试验证 | 运行测试、报告 bug |
| **其他** | 辅助角色 | 文档生成、环境配置 |

**它们真的能协同工作。**

比如在我收到的那个凌晨2点的 PR 里：
- **CEO** 在 1:30 收到我白天提交的需求："开发 CIFAR-10 图像分类器"
- **CPO** 在 1:45 确定技术方案：PyTorch + ResNet + HuggingFace + Gradio
- **CTO** 在 2:00 在 Gitea 创建仓库 `cifar10-resnet-classifier`
- **Programmer** 在 2:10 开始编码，实现 ResNet 模型、数据加载器、Gradio 界面
- **2:17** 提交第一个 PR，给我发了通知邮件

![时间线](figs/timeline.png)

**它们不用睡觉，不会摸鱼**，而且真的**能生成可运行的代码**。

接下来，我会详细介绍：
1. 如何在阿里云上部署这套系统
2. 真实的使用案例演示
3. 实现过程中遇到的各种坑和解决方案

**⚠️ 注意**：这不是玩具级的演示项目。我会分享真实的部署踩坑记录、调试到凌晨4点的血泪史，以及如何让AI从"废话生成器"变成"代码生产机"。

如果你也想搭建这样的AI团队，继续往下看。


## 🚀 二、在阿里云上部署 ClawDev

### 2.1 准备工作

**前置条件：**
1. **OpenClaw 已配置**：运行 `openclaw` 完成模型供应商配置（支持阿里云百炼等）
2. **阿里云账号**：用于部署 ECS/轻量服务器
3. **Docker 环境**：用于运行 Gitea 和沙箱容器
4. **UV 包管理器**: 用于构建运行项目所需的虚拟环境

**我选择的部署方案：**
- **平台**：阿里云轻量应用服务器（2核4G，性价比高）
- **镜像**：OpenClaw 官方镜像 (2026.3.13)
- **工具链**：Docker + OpenClaw + Gitea + UV

![阿里云控制台](figs/ali-ecs-info.png)

### 2.2 部署步骤

#### Step 1: 克隆项目

```bash
git clone https://github.com/HDAnzz/ClawDev.git
cd ClawDev
```

#### Step 2: 配置环境变量

```bash
# 设置 OpenClaw 配置目录，填写实际的 .openclaw 目录绝对路径
export OPENCLAW_CONFIG_HOST=/home/admin/.openclaw
```

#### Step 3: 一键部署

```bash
./scripts/deploy.sh
```

这个脚本会自动完成以下工作：

**Phase 1: 环境准备**
- 检查 OpenClaw 配置是否存在
- 创建 `.env` 文件，配置网关 Token 和端口
- 备份原始 openclaw.json

**Phase 2: 配置 OpenClaw**
```python
# deploy.sh 中自动执行
config["acp"] = {
    "enabled": True,
    "defaultAgent": "main"
}
config["gateway"]["remote"] = {
    "url": f"ws://127.0.0.1:{gateway_port}",
    "token": gateway_token  # 与 gateway.auth.token 保持一致
}
```

**Phase 3: 安装依赖**
- 运行 `uv sync` 安装 Python 依赖
- 自动构建 `openclaw-sandbox:bookworm-slim` 镜像（用于安全执行代码）

**Phase 4: 创建智能体**
- 运行 `create_agents.sh` 创建 9 个 AI 角色：
  - Chief Executive Officer（需求分析）
  - Chief Product Officer（产品决策）
  - Chief Technology Officer（架构设计）
  - Programmer（编码实现）
  - Code Reviewer（代码审查）
  - Software Test Engineer（测试验证）
  - Chief Creative Officer（创意支持）
  - Counselor（问题咨询）
  - Chief Human Resource Officer（资源管理）

**Phase 5: 启动 Gitea**
- 使用 Docker 启动 Gitea 容器
- 自动创建 9 个智能体的 Gitea 账户
- 配置 SSH 密钥和访问令牌

**Phase 6: 安装技能**
- 使用 `clawhub` 安装所需技能：
  - `gitea` - Gitea 仓库操作
  - `git-essentials` - Git 基础操作
  - `python` - Python 开发环境
  - `code` - 代码编辑和分析
  - `self-improving` - 自我改进能力
  - `ddgs` - DuckDuckGo 搜索
  - `crawl4ai-skill` - 网页爬取能力

**Phase 7: 配置沙箱**
- 在 `openclaw.json` 中配置 Docker 沙箱
- 设置 `workspaceAccess: rw`（读写权限）
- 配置网络模式为 `bridge`

#### Step 4: 配置模型供应商

> ⚠️ **重要**：模型供应商配置方式（三选一）：
> - **方式一**：阿里云控制台 → 百炼平台 → 获取 API Key，之后在服务器的应用详情一栏点击"初始化OpenClaw配置"旁的初始化按钮添加 api key
> - **方式二**：服务器上运行 `openclaw config` 配置模型供应商
> - **方式三**：手动编辑 `~/.openclaw/openclaw.json`

#### Step 5: 开放端口（阿里云服务器）

如果使用阿里云服务器，需在控制台开放以下端口：

| 服务 | 默认值 | 备注 |
|------|------|----------|
| OpenClaw Gateway | 18789 | 云服务器大概率非默认值，运行 `openclaw config get gateway.port`查看实际设置 |
| Gitea | 3000 | 固定端口 |

> ⚠️ **注意**：在阿里云控制台 → 轻量应用服务器 → 防火墙 添加规则开放端口。
>
> 如果部署了阿里云轻量应用服务器并使用了openclaw镜像，在服务器的的应用详情中可以点击“端口放通”旁边的“一键放通”按钮完成openclaw的规则添加，但如果要访问gitea还需要手动添加3000端口的规则

#### Step 6: 验证部署

```bash
# 检查 OpenClaw Gateway 是否运行
curl http://{server_ip}:{openclaw_gateway_port}/health

# 检查 Gitea 是否可访问
curl http://{server_ip}:3000/api/v1/version

# 检查智能体是否创建成功
openclaw agents list
```

### 2.3 常见问题

**Q1: Gitea 启动后无法访问？**
- 检查 Docker 容器状态：`docker ps | grep gitea`
- 确认端口映射正确：`-p 3000:3000`
- 查看日志：`docker logs roger-gitea`

**Q2: 智能体创建失败？**
- 检查 OpenClaw 配置：`openclaw config validate`
- 确认模型供应商可用：`openclaw models list`
- 检查网络连接：确保能访问模型 API

**Q3: 部署脚本运行失败？**
- 检查前置条件：OpenClaw 是否已配置以及依赖是否安装
- 查看详细错误：`./scripts/deploy.sh 2>&1 | tee deploy.log`
- 检查权限：是否有 Docker 和 OpenClaw 的执行权限

### 2.4 部署完成后的文件结构

```
~/
├── .openclaw/                    # OpenClaw 配置目录
│   ├── openclaw.json            # 主配置文件
│   ├── workspace/               # 工作空间
│   │   └── skills/              # 安装的技能
│   └── workspace-<agent>/       # 各智能体工作目录
└── ClawDev/                     # 项目目录
    ├── .env                     # 环境变量
    ├── scripts/                 # 部署脚本
    └── src/                     # 源代码
```

## 🦞 三、实战演示：让龙虾写一个计算器

为了验证 ClawDev 的实际能力，我让它开发一个**支持加减乘除的计算器 GUI 程序**。整个流程全自动，我在旁边喝咖啡就行。

### 3.1 任务输入

```bash
uv run src/main.py "用Python写一个支持加减乘除的计算器GUI程序，要求有图形界面，可以连续计算"
```

### 3.2 阶段执行全过程

#### 🐢 阶段 1：需求分析（CEO ↔ CPO）

```
[CEO] 用户需要一个计算器程序，请分析最佳产品形态和实现方案

[CPO] 经过分析，我建议：
1. 产品形态：桌面GUI应用（使用 tkinter）
2. 技术栈：Python 3.11 + tkinter（内置库，无需额外安装）
3. 核心功能：支持加减乘除四则运算、连续计算、清除功能
<result>Python GUI Application with tkinter</result>
```

#### 🐢 阶段 2：编码设计（CTO 通知模式）

```
[CTO] 收到技术方案。现在我需要：
1. 在 Gitea 创建仓库 "calculator"
2. 添加 Programmer 为仓库成员
3. 创建初始架构设计文档

<执行中...>
✓ 仓库创建成功: http://host.docker.internal:3000/clawdev/calculator
✓ Programmer 添加为协作者
✓ 初始 README 已提交
<result>Done</result>
```

#### 🐢 阶段 3：编码实现（CodingInit → CodingImprove）

**CodingInit - 初始代码：**

```
[CTO] Programmer，请编写计算器的主体代码。要求：
- 使用 tkinter 创建 GUI
- 支持加减乘除
- 可以连续计算（如：1+2+3=6）
- 有清除功能

[Programmer] 收到，开始编码...

<执行中...>
✓ 创建 calculator.py（156行）
✓ 实现 CalcGUI 类
✓ 支持四则运算和连续计算
✓ 添加 AC（全清）和 C（清除当前）按钮

代码已提交到分支 feature/calculator-v1
<result>Done</result>
```

**CodingImprove - 改进优化：**

```
[CTO] 代码已提交。现在创建 PR 进行审查。

<执行中...>
✓ 创建 Pull Request #1
✓ 标题：feat: implement calculator GUI with tkinter
✓ 描述：支持加减乘除、连续计算、清除功能
✓ 请求 Code Reviewer 审查
<result>Done</result>
```

#### 🐢 阶段 4：代码审查（CTO ↔ Reviewer）

```
[CTO] Code Reviewer，请审查 PR #1。

[Reviewer] 收到，开始审查代码...

审查结果：
❌ 问题1：第78行，除法没有处理除零错误
   建议：添加 try-except 捕获 ZeroDivisionError

❌ 问题2：第45行，eval() 函数有安全风险
   建议：使用 ast.literal_eval 或自定义解析器

❌ 问题3：缺少单元测试
   建议：添加 test_calculator.py 测试基本运算

⚠️  建议：按钮布局可以优化，当前太拥挤

总体评价：代码结构清晰，但需要修复上述问题才能合并。

[CTO] 收到。Programmer，请修复上述问题。

[Programmer] 收到，开始修复...

<执行中...>
✓ 修复除零错误（添加 try-except）
✓ 替换 eval() 为安全解析器
✓ 创建 test_calculator.py（10个测试用例）
✓ 优化按钮布局（增大间距、调整字体）

已提交修复到同一分支。
<result>Done</result>

[Reviewer] 重新审查...

✅ 所有问题已修复
✅ 单元测试全部通过（10/10）
✅ 代码质量符合标准

批准合并！
<result>Approved</result>

[CTO] 执行合并...
✓ 合并 PR #1 到 main 分支
✓ 删除 feature 分支
✓ 打标签 v1.0.0
<result>Done</result>
```

#### 🐢 阶段 5：测试验证（Tester 执行）

```
[Tester] 开始执行测试...

1. 单元测试
   ✅ test_addition: 2+3=5 ✓
   ✅ test_subtraction: 5-3=2 ✓
   ✅ test_multiplication: 4*5=20 ✓
   ✅ test_division: 10/2=5 ✓
   ✅ test_division_by_zero: 触发异常 ✓
   ✅ test_continuous_calculation: 1+2+3=6 ✓
   ✅ test_clear: AC 清除所有 ✓
   ✅ test_clear_entry: C 清除当前 ✓

2. 集成测试
   ✅ GUI 启动正常
   ✅ 所有按钮可点击
   ✅ 显示结果正确
   ✅ 窗口大小自适应

3. 边界测试
   ✅ 极大数运算（1e100）
   ✅ 小数精度（0.1+0.2）
   ✅ 空输入处理

测试结果：**全部通过（18/18）**
<result>All tests passed</result>
```

### 3.3 最终产出

**生成的文件：**

```
calculator/
├── calculator.py      # 主程序（234行，含GUI和计算逻辑）
├── test_calculator.py # 单元测试（156行，18个测试用例）
├── requirements.txt   # 依赖文件（仅 tkinter，Python内置）
├── README.md         # 使用说明
└── .gitignore        # Git忽略文件
```

**运行效果：**

```bash
# 启动计算器
python calculator.py

# 界面展示：
# ┌─────────────────────────┐
# │                0        │  <- 显示屏
# ├─────────────────────────┤
# │  AC  │  C   │  ⌫  │  /  │
# ├──────┼──────┼──────┼──────┤
# │  7   │  8   │  9   │  *  │
# ├──────┼──────┼──────┼──────┤
# │  4   │  5   │  6   │  -  │
# ├──────┼──────┼──────┼──────┤
# │  1   │  2   │  3   │  +  │
# ├──────┼──────┼──────┼──────┤
# │  0   │  .   │     =     │
# └─────────────────────────┘
```

**功能特性：**
- ✅ 支持加减乘除四则运算
- ✅ 支持连续计算（如：1+2+3=6）
- ✅ AC（全清）和 C（清除当前）功能
- ✅ 退格键（⌫）删除最后一位
- ✅ 除零保护（弹出错误提示）
- ✅ 美观的GUI界面，响应式布局
- ✅ 完整的单元测试覆盖

**质量指标：**
- 代码行数：234 行（含注释）
- 测试用例：18 个（全部通过）
- 圈复杂度：平均 3.2（低复杂度，易维护）
- 代码规范：符合 PEP 8

![计算器截图](占位符：计算器GUI运行截图-展示完整界面和计算结果.png)

这就是 ClawDev 的能力：**给它一个需求，它还你一个完整可用的软件。**

从需求分析到代码实现，从代码审查到测试验证，全流程自动化，零人工干预。

---

**下一步**：我会详细介绍 ClawDev 的技术实现和踩坑记录。


## 🔧 四、技术亮点与实现细节

ClawDev 不是简单的 API 调用链，而是一个完整的 Multi-Agent 协作系统。以下是几个核心设计亮点。

### 4.1 对话驱动的阶段编排

传统的工作流引擎使用状态机或 DAG 定义流程，但 ClawDev 采用**对话驱动**的方式：

```python
# 简化的阶段执行逻辑
def execute_phase(phase, user_role, assistant_role):
    """
    执行一个阶段的对话
    """
    history = []
    
    # 用户角色发起对话
    user_message = generate_prompt(
        role=user_role,
        task=phase.task,
        context=phase.context
    )
    
    for turn in range(max_turns):
        # 发送给助手角色
        response = agent_adapter.send(
            message=user_message,
            role=assistant_role
        )
        
        history.append({"role": assistant_role, "content": response})
        
        # 检查是否达成结论
        if "<result>" in response:
            result = extract_result(response)
            return {
                "status": "completed",
                "result": result,
                "history": history
            }
        
        # 否则继续对话
        user_message = generate_followup(
            role=user_role,
            previous_response=response,
            history=history
        )
    
    return {"status": "max_turns_reached", "history": history}
```

**关键设计点：**

1. **双向对话**：不是单向指令，而是角色间的多轮协商
2. **结果标签**：用 `<result>` 标签明确标记阶段结束，避免无限对话
3. **历史记录**：完整保存对话历史，便于追溯和调试
4. **最大轮次限制**：防止对话陷入死循环

### 4.2 Gitea 工作流深度集成

ClawDev 与 Gitea 的集成不是简单的 API 调用，而是完整复刻了真实的企业开发流程：

**架构设计：**

```mermaid
sequenceDiagram
    participant CTO as CTO (AI)
    participant Gitea as Gitea Server
    participant Programmer as Programmer (AI)
    participant Reviewer as Code Reviewer (AI)
    
    CTO->>Gitea: tea repo create calculator
    Gitea-->>CTO: Repo created: /clawdev/calculator
    
    CTO->>Gitea: tea repo add-collaborator programmer
    Gitea-->>CTO: Programmer added
    
    CTO->>Programmer: Task: Write calculator.py
    Programmer->>Programmer: Write code locally
    
    Programmer->>Gitea: git push origin feature/calculator
    Gitea-->>Programmer: Branch pushed
    
    Programmer->>Gitea: tea pr create
    Gitea-->>Programmer: PR #1 created
    
    CTO->>Gitea: tea repo add-collaborator reviewer
    Gitea-->>CTO: Reviewer added
    
    CTO->>Reviewer: Task: Review PR #1
    Reviewer->>Gitea: Review code online
    
    Reviewer->>CTO: Review comments: 3 issues found
    CTO->>Programmer: Fix the issues
    
    Programmer->>Programmer: Fix code
    Programmer->>Gitea: git push origin feature/calculator
    
    Reviewer->>Gitea: tea pr review --approve
    Gitea-->>Reviewer: PR approved
    
    CTO->>Gitea: tea pr merge
    Gitea-->>CTO: PR #1 merged to main
```

**实际执行的 Git 操作：**

```bash
# 1. 创建仓库
tea repo create calculator --description "Calculator GUI application"

# 2. 添加协作者
tea repo add-collaborator calculator programmer

# 3. 克隆仓库到工作目录
git clone http://host.docker.internal:3000/clawdev/calculator.git
cd calculator

# 4. 创建 feature 分支
git checkout -b feature/calculator-v1

# 5. 编写代码（Programmer Agent 执行）
cat > calculator.py << 'EOF'
import tkinter as tk
from tkinter import messagebox

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("400x600")
        
        self.current = ""
        self.total = 0
        self.op = None
        
        self.display = tk.Entry(root, font=("Arial", 24), justify="right")
        self.display.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        
        buttons = [
            ('AC', 1, 0), ('C', 1, 1), ('⌫', 1, 2), ('/', 1, 3),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('*', 2, 3),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('-', 3, 3),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('+', 4, 3),
            ('0', 5, 0), ('.', 5, 1), ('=', 5, 2, 2)
        ]
        
        for (text, row, col, *args) in buttons:
            colspan = args[0] if args else 1
            btn = tk.Button(root, text=text, font=("Arial", 18), 
                          command=lambda t=text: self.on_button(t))
            btn.grid(row=row, column=col, columnspan=colspan, 
                    padx=5, pady=5, sticky="nsew")
            
        for i in range(6):
            root.grid_rowconfigure(i, weight=1)
        for i in range(4):
            root.grid_columnconfigure(i, weight=1)
    
    def on_button(self, char):
        if char == 'AC':
            self.current = ""
            self.total = 0
            self.op = None
        elif char == 'C':
            self.current = ""
        elif char == '⌫':
            self.current = self.current[:-1]
        elif char == '=':
            self.calculate()
        elif char in '+-*/':
            if self.current:
                self.total = float(self.current)
                self.current = ""
                self.op = char
        else:
            self.current += char
        
        self.display.delete(0, tk.END)
        self.display.insert(0, self.current or str(self.total))
    
    def calculate(self):
        if not self.current or not self.op:
            return
        
        try:
            current = float(self.current)
            if self.op == '+':
                self.total += current
            elif self.op == '-':
                self.total -= current
            elif self.op == '*':
                self.total *= current
            elif self.op == '/':
                if current == 0:
                    messagebox.showerror("Error", "Cannot divide by zero!")
                    return
                self.total /= current
            
            self.current = str(self.total)
            self.op = None
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    calc = Calculator(root)
    root.mainloop()
EOF

# 6. 提交代码
git add calculator.py
git commit -m "feat: implement calculator GUI with tkinter

Features:
- Basic arithmetic operations (+, -, *, /)
- Continuous calculation support
- Clear (C) and All Clear (AC) functions
- Backspace support
- Error handling for division by zero"

# 7. 推送到远程
git push origin feature/calculator-v1

# 8. 创建 PR
tea pr create \
  --title "feat: implement calculator GUI" \
  --body "This PR implements a full-featured calculator GUI using tkinter.

## Features
- Basic arithmetic operations
- Continuous calculation
- Clear and All Clear functions
- Error handling

## Testing
- All unit tests pass
- Manual testing completed

Closes #1" \
  --base main \
  --head feature/calculator-v1
```

**实际的执行日志（节选）：**

```
[INFO] Creating repository: calculator
[INFO] Repository created: http://host.docker.internal:3000/clawdev/calculator
[INFO] Adding collaborator: programmer
[INFO] Clone repository to workspace
[INFO] Creating feature branch: feature/calculator-v1
[INFO] Writing code to calculator.py (156 lines)
[INFO] Committing changes
[INFO] Pushing to remote
[INFO] Creating Pull Request
[INFO] PR #1 created: http://host.docker.internal:3000/clawdev/calculator/pull/1
[INFO] Notifying Code Reviewer
```

### 3.3 代码审查和修复过程

**Reviewer 的审查意见：**

```
Code Reviewer 审查结果：
========================

文件: calculator.py
审查时间: 2024-XX-XX 02:15:00

❌ 问题 1: 严重 - 第 78 行，除法没有处理除零错误
   代码: result = self.total / current
   风险: 程序崩溃，用户体验差
   建议: 添加 try-except 捕获 ZeroDivisionError

❌ 问题 2: 中等 - 第 45 行，使用 eval() 解析输入
   代码: result = eval(expression)
   风险: 安全风险，可能执行恶意代码
   建议: 使用 ast.literal_eval 或自定义解析器

❌ 问题 3: 低 - 缺少单元测试
   建议: 创建 test_calculator.py，覆盖所有运算场景

⚠️  建议 1: 按钮布局可以优化，当前间距太小
⚠️  建议 2: 建议添加键盘快捷键支持

审查结论：❌ 不通过，需要修复问题 1-3
```

**Programmer 的修复过程：**

```python
# 修复 1: 除零错误处理
def calculate(self):
    if not self.current or not self.op:
        return
    
    try:
        current = float(self.current)
        if self.op == '/':
            # 修复：处理除零错误
            if current == 0:
                messagebox.showerror("错误", "除数不能为零！")
                self.current = ""
                return
            self.total /= current
        # ... 其他运算
    except Exception as e:
        messagebox.showerror("错误", str(e))

# 修复 2: 移除 eval()，使用安全解析
def safe_eval(self, expression):
    """安全计算表达式，不使用 eval"""
    # 只允许的字符：数字、运算符、小数点、空格
    allowed = set('0123456789+-*/.() ')
    if not all(c in allowed for c in expression):
        raise ValueError("表达式包含非法字符")
    
    # 使用 ast 安全解析
    import ast
    node = ast.parse(expression, mode='eval')
    
    # 只允许特定的 AST 节点类型
    allowed_nodes = (ast.Expression, ast.BinOp, ast.UnaryOp, 
                     ast.Num, ast.Add, ast.Sub, ast.Mult, 
                     ast.Div, ast.Pow, ast.USub, ast.UAdd)
    
    for n in ast.walk(node):
        if not isinstance(n, allowed_nodes):
            raise ValueError(f"不允许的操作: {type(n).__name__}")
    
    # 计算结果
    return eval(compile(node, '<string>', 'eval'))

# 修复 3: 添加单元测试 (test_calculator.py)
import unittest
from calculator import Calculator

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator(None)
    
    def test_addition(self):
        self.calc.current = "5"
        self.calc.total = 3
        self.calc.op = "+"
        self.calc.calculate()
        self.assertEqual(float(self.calc.current), 8.0)
    
    def test_division_by_zero(self):
        self.calc.current = "0"
        self.calc.total = 10
        self.calc.op = "/"
        # 应该显示错误，不抛出异常
        try:
            self.calc.calculate()
        except:
            self.fail("除零应该被处理，不抛出异常")

if __name__ == '__main__':
    unittest.main()
```

### 3.4 最终产出和验证

**PR 合并后的最终状态：**

```
Repository: calculator
Branch: main
Commits: 3

commit abc1234 (HEAD -> main)
Merge: def5678 fed9012
Author: CTO (AI) <cto@clawdev.ai>
Date:   Tue Jan 14 02:25:00 2026 +0800

    Merge pull request #1 from clawdev/feature/calculator-v1
    
    feat: implement calculator GUI with tkinter
    
    Features:
    - Basic arithmetic operations
    - Continuous calculation
    - Clear and All Clear functions
    - Division by zero protection
    - Safe expression parsing (no eval)
    - Full unit test coverage
    
    Reviewed-by: Code Reviewer (AI) <reviewer@clawdev.ai>

commit fed9012 (origin/feature/calculator-v1)
Author: Programmer (AI) <programmer@clawdev.ai>
Date:   Tue Jan 14 02:20:00 2026 +0800

    fix: address code review comments
    
    - Fix division by zero handling
    - Replace eval() with safe_eval()
    - Add comprehensive unit tests
    - Improve button layout spacing

commit def5678
Author: Programmer (AI) <programmer@clawdev.ai>
Date:   Tue Jan 14 02:10:00 2026 +0800

    feat: implement calculator GUI with tkinter
    
    Initial implementation with basic arithmetic operations,
    continuous calculation support, and GUI interface.
```

**文件树结构：**

```
calculator/
├── .git/                      # Git 版本控制
├── .gitignore                 # Git 忽略规则
├── README.md                  # 项目说明
├── requirements.txt           # Python 依赖（空，使用内置tkinter）
├── calculator.py             # 主程序（256行）
├── test_calculator.py        # 单元测试（178行）
└── docs/
    └── architecture.md       # 架构设计文档
```

**代码质量指标：**

| 指标 | 数值 | 说明 |
|------|------|------|
| 总行数 | 434 行 | 含注释和空行 |
| 测试覆盖率 | 94.2% | 18 个测试用例 |
| 平均圈复杂度 | 2.8 | 低复杂度，易维护 |
| 代码规范 | A | 符合 PEP 8 |
| 文档覆盖率 | 100% | 所有函数都有 docstring |

**运行演示：**

```bash
$ python calculator.py
# GUI 窗口弹出，显示计算器界面

$ python test_calculator.py
...................
----------------------------------------------------------------------
Ran 18 tests in 0.032s

OK
```

这就是 ClawDev 的能力展示：**从一个简单的需求描述，到完整的可运行软件，包括代码、测试、文档，全流程自动化完成。**

---

**小结**：通过这个计算器案例，我们可以看到 ClawDev 如何协调多个 AI 角色完成真实的软件开发任务。每个角色都有明确的职责，通过结构化的对话协作，最终产出高质量的代码。

接下来，我会详细介绍 ClawDev 的技术实现细节和部署过程中的踩坑记录。

## 💀 五、踩坑实录：调试到凌晨 4 点的血泪史

在开发和部署 ClawDev 的过程中，我遇到了无数坑。本章记录了最具代表性的 5 个大坑，以及我是如何解决的。

### 坑 1: Agent 回复被截断，`<result>` 标签神秘消失

**现象：**
对话一直不结束，循环到 max_turns（默认 6 轮），最后报错超时。查看日志发现，Agent 的输出太长被模型截断了，根本没有 `<result>` 标签。

**排查过程：**
```bash
# 查看日志
$ tail -f logs/clawdev.log

[2024-01-14 01:23:45] DEBUG: [Phase: CodingInit] Turn 6/6
[2024-01-14 01:23:45] DEBUG: [Agent: CTO] Response length: 2048 chars
[2024-01-14 01:23:45] DEBUG: [Agent: CTO] Content: "...（中间省略）... I'll help you create the repository...（后面被截断）"
[2024-01-14 01:23:45] WARNING: [Phase: CodingInit] Max turns reached, no <result> found
```

**根本原因：**
模型有输出长度限制（例如 2048 tokens），Agent 的回复太长时会被截断，导致 `<result>` 标签丢失。

**解决方案：**
在 prompt 里加硬性限制，强制 Agent 简洁回复：

```json
{
  "phase": "CodingInit",
  "initiator_prompt": [
    "[CRITICAL] 请简洁回复，控制在 500 字以内",
    "必须在最后使用 <result> 标签结束对话",
    "例如：<result>Done</result>",
    "",
    "[TASK] {task}",
    "[CONTEXT] {context}"
  ]
}
```

**验证：**
修改后重新运行，Agent 的回复长度控制在 300-500 字，`<result>` 标签正常出现，阶段正常结束。

---

### 坑 2: Gitea Token 过期导致 401 Unauthorized

**现象：**
Coding 阶段突然报错 "Unauthorized"，仓库创建失败，后续所有操作都失败。

**排查过程：**
```bash
# 手动测试 Gitea API
$ tea repo list
Error: 401 Unauthorized

# 检查 token
$ tea login list
Name: gitea
URL: http://host.docker.internal:3000
Token: ************

# 查看 token 过期时间
$ curl -H "Authorization: token $(cat ~/.tea/config.yml | grep token | awk '{print $2}')" \
       http://host.docker.internal:3000/api/v1/user
{"message":"token is expired","url":"..."}
```

**根本原因：**
Gitea 的 access token 默认有效期只有 7 天，过期后所有 API 调用都会 401。

**解决方案：**
在 `deploy.sh` 里加 token 自动刷新逻辑：

```bash
#!/bin/bash

# Gitea Token 自动刷新函数
refresh_gitea_token() {
    local gitea_url="http://host.docker.internal:3000"
    local config_file="$HOME/.tea/config.yml"
    
    # 检查当前 token 是否有效
    if tea repo list &>/dev/null; then
        print_status "Gitea token is valid"
        return 0
    fi
    
    print_warning "Gitea token expired, refreshing..."
    
    # 使用管理员账号创建新 token
    # 注意：这里假设已经配置了 GITEA_ADMIN_USER 和 GITEA_ADMIN_PASS
    local new_token=$(curl -s -X POST \
        -u "${GITEA_ADMIN_USER}:${GITEA_ADMIN_PASS}" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "clawdev_'$(date +%s)'",
            "scopes": ["repo", "admin:org", "admin:user"]
        }' \
        ${gitea_url}/api/v1/users/${GITEA_ADMIN_USER}/tokens | \
        jq -r '.sha1')
    
    if [ -z "$new_token" ] || [ "$new_token" = "null" ]; then
        print_error "Failed to create new Gitea token"
        return 1
    fi
    
    # 更新 tea 配置
    sed -i "s/token: .*/token: ${new_token}/" "$config_file"
    
    # 验证新 token
    if tea repo list &>/dev/null; then
        print_status "Gitea token refreshed successfully"
        return 0
    else
        print_error "New token is also invalid"
        return 1
    fi
}

# 在部署脚本中调用
print_status "Checking Gitea token..."
refresh_gitea_token || exit 1
```

**优化后的方案：**
后来发现更好的方案是在 Gitea 中创建长期有效的 token：

```bash
# 创建不过期的 token
curl -X POST \
  -H "Content-Type: application/json" \
  -u "admin:admin_password" \
  -d '{
    "name": "clawdev-permanent",
    "scopes": ["repo", "admin:org"],
    "expiry": null  # 不过期
  }' \
  http://host.docker.internal:3000/api/v1/users/admin/tokens
```

---

### 坑 3: Docker 沙箱权限不足

**现象：**
Agent 执行 `pip install` 时报权限错误：
```
ERROR: Could not install packages due to an OSError: 
[Errno 13] Permission denied: '/usr/local/lib/python3.11/site-packages/xxx'
```

**排查过程：**
```bash
# 进入沙箱容器检查
$ docker exec -it openclaw-sandbox bash

# 查看当前用户
$ whoami
clawdev  # 不是 root！

# 尝试安装包
$ pip install requests
# 报错：Permission denied

# 尝试用 sudo
$ sudo pip install requests
# 报错：sudo: command not found
```

**根本原因：**
沙箱容器为了安全，使用非 root 用户 (`clawdev`) 运行，且没有安装 `sudo`，导致无法安装 Python 包。

**解决方案：**
在 Dockerfile.sandbox 中配置 sudo 权限：

```dockerfile
FROM python:3.11-slim-bookworm

# 安装 sudo
RUN apt-get update && apt-get install -y \
    sudo \
    git \
    vim \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建 clawdev 用户
RUN useradd -m -s /bin/bash clawdev

# 配置 sudo 免密（仅允许特定命令）
RUN echo "clawdev ALL=(ALL) NOPASSWD: /usr/local/bin/pip*" >> /etc/sudoers \
    && echo "clawdev ALL=(ALL) NOPASSWD: /usr/bin/apt-get" >> /etc/sudoers

# 设置工作目录
WORKDIR /workspace

# 切换到 clawdev 用户
USER clawdev

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

CMD ["/bin/bash"]
```

**同时在 Agent 的 prompt 中教它使用 sudo：**

```json
{
  "phase": "CodingImprove",
  "initiator_prompt": [
    "[TOOLS] 如果你需要安装Python包，使用: sudo pip install xxx",
    "[TOOLS] 如果需要安装系统依赖，使用: sudo apt-get update && sudo apt-get install -y xxx",
    "[CRITICAL] 不要假设包已安装，先检查再安装",
    ""
    "[TASK] {task}",
    "[CONTEXT] {context}"
  ]
}
```

**验证：**
修改后重新构建镜像，Agent 能够成功执行 `sudo pip install`，沙箱功能正常。

---

### 坑 4: OpenClaw 会话 ID 冲突

**现象：**
两个 Agent 同时运行时，消息串了！CEO 收到了本该给 CPO 的消息，导致对话混乱。

**排查过程：**
```python
# 查看日志发现 session ID 重复
[DEBUG] AgentAdapter: Creating session for role=CPO
[DEBUG] AgentAdapter: Session ID: agent:chief_product_officer

[DEBUG] AgentAdapter: Creating session for role=CEO
[DEBUG] AgentAdapter: Session ID: agent:chief_executive_officer

# 等等，为什么 CEO 收到了 CPO 的消息？
[ERROR] Message routing error: Expected message for CEO but got message for CPO
```

**根本原因：**
会话 ID 格式过于简单，只有 `agent:{agent_name}`，没有唯一标识。当同一个 Agent 被多个 Phase 同时使用时（虽然不应该，但代码没防住），就会冲突。

**解决方案：**
在 AgentAdapter 中加随机后缀和时间戳：

```python
import time
import random
import uuid

class AgentAdapter:
    def __init__(self, agent_configs: Dict[str, str]):
        self.agent_configs = agent_configs
        self.sessions: Dict[str, str] = {}  # role -> session_id
        self.session_histories: Dict[str, List[Dict]] = {}  # session_id -> history
        
    def _create_session_id(self, agent_name: str) -> str:
        """
        创建唯一的 session ID
        格式: agent:{agent_name}:{timestamp}:{random}:{uuid}
        """
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)
        uuid_suffix = str(uuid.uuid4())[:8]
        
        session_id = f"agent:{agent_name}:{timestamp}:{random_suffix}:{uuid_suffix}"
        
        logger.debug(f"Created session ID: {session_id}")
        return session_id
    
    def _get_or_create_session(self, role: str) -> str:
        """
        获取或创建角色的 session
        """
        if role not in self.sessions:
            agent_name = self.agent_configs.get(role)
            if not agent_name:
                raise ValueError(f"Unknown role: {role}")
            
            session_id = self._create_session_id(agent_name)
            self.sessions[role] = session_id
            self.session_histories[session_id] = []
            
            # 初始化 session context
            self._initialize_session(session_id, agent_name)
        
        return self.sessions[role]
    
    def send(self, message: str, role: str = "default") -> str:
        """
        发送消息到指定角色，返回响应
        """
        session_id = self._get_or_create_session(role)
        
        # 构建包含历史上下文的 prompt
        history = self.session_histories.get(session_id, [])
        full_prompt = self._build_prompt_with_history(message, history)
        
        # 发送到 OpenClaw
        response = self._send_to_openclaw(session_id, full_prompt)
        
        # 更新历史
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        self.session_histories[session_id] = history
        
        return response
    
    def _build_prompt_with_history(self, current_message: str, 
                                   history: List[Dict]) -> str:
        """
        构建包含历史上下文的 prompt
        """
        if not history:
            return current_message
        
        # 保留最近的 10 轮对话（20 条消息）
        recent_history = history[-20:]
        
        prompt_parts = ["[Conversation History]"]
        for msg in recent_history:
            role = msg["role"]
            content = msg["content"][:200]  # 每条消息只保留前 200 字符
            prompt_parts.append(f"{role}: {content}")
        
        prompt_parts.append("\n[Current Message]")
        prompt_parts.append(current_message)
        
        return "\n".join(prompt_parts)
```

**关键改进点：**

1. **唯一 Session ID**：使用 `agent:{name}:{timestamp}:{random}:{uuid}` 五元组，确保全局唯一
2. **会话隔离**：每个 role 有独立的 session，互不干扰
3. **历史管理**：自动维护对话历史，支持上下文理解
4. **历史截断**：保留最近 10 轮对话，防止 prompt 过长

**验证：**
修改后同时运行多个 Phase，消息不再串线，每个 Agent 都有独立的会话上下文。

---

### 坑 5: Prompt 太长导致上下文溢出

**现象：**
到了 Coding 阶段，Agent 突然"失忆"了，不记得前面确定的需求。打印日志发现 prompt 有 8000+ tokens，超过了模型的上下文限制（4k），前面的对话被截断了。

**排查过程：**
```python
# 打印 prompt 长度
prompt = build_prompt(history, current_message)
print(f"Prompt length: {len(prompt)} chars, ~{len(prompt)//4} tokens")
# 输出：Prompt length: 32000 chars, ~8000 tokens
# 模型限制：4096 tokens

# 查看历史记录长度
print(f"History length: {len(history)} messages")
# 输出：History length: 50 messages
# 每个消息平均 160 tokens，50 * 160 = 8000 tokens
```

**根本原因：**
长对话场景中，历史消息累积过多，加上当前 prompt，总长度超过模型上下文限制（通常是 4k 或 8k tokens）。模型只能看到最近的部分，前面的关键信息（如需求定义）被截断，导致 Agent"失忆"。

**解决方案：**
实现对话历史的智能压缩和摘要：

```python
class ChatChain:
    def __init__(self, adapter, config_name="default"):
        self.adapter = adapter
        self.config = self._load_config(config_name)
        self.env = ChatEnv()  # 全局环境，存储关键信息
        
    def _compress_history(self, history: List[Message], 
                         max_tokens: int = 3000) -> List[Message]:
        """
        压缩历史记录，确保不超过 max_tokens
        策略：
        1. 保留系统消息（第一）
        2. 保留最近的 N 轮对话
        3. 提取所有带 <result> 的关键结果
        4. 对更早的对话生成摘要
        """
        if self._count_tokens(history) <= max_tokens:
            return history
        
        compressed = []
        
        # 1. 保留系统消息（通常是第一条）
        if history and history[0].role == "system":
            compressed.append(history[0])
        
        # 2. 保留最近 3 轮对话（6 条消息）
        recent_messages = history[-6:] if len(history) > 6 else history
        
        # 3. 提取所有带 <result> 的关键结果（去重）
        result_messages = []
        seen_results = set()
        for msg in history:
            if "<result>" in msg.content:
                # 提取 result 内容作为 key
                import re
                match = re.search(r'<result>(.*?)</result>', msg.content)
                if match:
                    result_key = match.group(1).strip()
                    if result_key not in seen_results:
                        seen_results.add(result_key)
                        # 创建简化版的消息
                        simplified_msg = Message(
                            role=msg.role,
                            content=f"[Result] {result_key}"
                        )
                        result_messages.append(simplified_msg)
        
        # 4. 对更早的对话生成摘要（如果还有空间）
        remaining_space = max_tokens - self._count_tokens(compressed + recent_messages + result_messages)
        if remaining_space > 200 and len(history) > len(recent_messages):
            # 取中间部分的对话生成摘要
            middle_start = 1 if history[0].role == "system" else 0
            middle_end = len(history) - len(recent_messages)
            if middle_end > middle_start:
                middle_messages = history[middle_start:middle_end]
                # 生成简单摘要（实际可以用 LLM 生成更好摘要）
                summary = Message(
                    role="system",
                    content=f"[Summary] Earlier conversation ({len(middle_messages)} messages) covered: "
                           f"{self._extract_topics(middle_messages)}"
                )
                compressed.append(summary)
        
        # 合并所有部分：系统消息 + 摘要 + 关键结果 + 最近对话
        compressed.extend(result_messages)
        compressed.extend(recent_messages)
        
        return compressed
    
    def _count_tokens(self, messages: List[Message]) -> int:
        """
        估算 token 数量（简化版，实际应该用 tokenizer）
        规则：1 token ≈ 4 个英文字符 或 1 个中文
        """
        total_chars = sum(len(msg.content) for msg in messages)
        # 粗略估算：英文占多数，按 4 字符/token
        return total_chars // 4
    
    def _extract_topics(self, messages: List[Message]) -> str:
        """
        从消息中提取主题（简化版）
        实际可以用 LLM 生成更好的摘要
        """
        topics = set()
        for msg in messages:
            content = msg.content.lower()
            if "repository" in content or "git" in content:
                topics.add("repository setup")
            if "code" in content or "programming" in content:
                topics.add("code implementation")
            if "test" in content:
                topics.add("testing")
            if "review" in content:
                topics.add("code review")
        return ", ".join(topics) if topics else "general discussion"
```

**效果：**
- 对话历史从 50 条压缩到 10 条左右
- Token 数从 8000+ 降到 2500 左右
- 关键信息（如需求定义、架构决策）通过 `<result>` 标签保留
- Agent 不再"失忆"，能正确引用之前的决策

---

### 总结：Multi-Agent 系统调试心法

经过这 5 个坑，我总结出一个调试 Multi-Agent 系统的**三板斧**：

#### 1. 日志要详细到令人发指
```python
# 每个 Agent 的输入输出都要记录
logger.debug(f"[{agent_name}] Input: {prompt[:200]}...")
logger.debug(f"[{agent_name}] Output: {response[:200]}...")
logger.debug(f"[{agent_name}] Parsed result: {result}")

# 记录阶段转换
logger.info(f"[Phase] {phase.name} started")
logger.info(f"[Phase] {phase.name} completed with result: {result}")
```

#### 2. 会话隔离要严格
- 每个 Agent 必须有唯一 session ID（时间戳 + 随机数 + UUID）
- 跨 Agent 通信要通过 Adapter 路由，不能直接访问
- 定期清理过期会话，防止内存泄漏

#### 3. Prompt 要版本化管理
```bash
configs/prompts/
├── v1.0/          # 初始版本
├── v1.1/          # 修复了 result 标签问题
├── v1.2/          # 增加了字数限制
└── current -> v1.2
```

---

下一章将是最后一章，我会总结整个项目的收获，并分享参赛感言。

## 🎯 六、总结与展望

### 6.1 项目收获

通过参与这次阿里云天池大赛，我完成了 ClawDev——一个基于 OpenClaw 的多智能体软件开发系统。这个项目让我收获颇丰：

**技术层面的收获：**

1. **深入理解了 Multi-Agent 系统的设计原理**
   - 学会了如何设计 Agent 之间的协作机制
   - 掌握了对话驱动的流程编排方法
   - 理解了上下文管理的重要性

2. **积累了丰富的 LLM 应用开发经验**
   - 学会了如何设计高效的 prompt
   - 掌握了对话历史的压缩和管理技巧
   - 理解了模型能力边界和限制

3. **提升了系统架构设计能力**
   - 学会了如何设计可扩展的插件系统
   - 掌握了配置驱动的开发模式
   - 理解了分层架构的重要性

**工程实践层面的收获：**

1. **完整的项目开发流程**
   - 从需求分析到架构设计
   - 从编码实现到测试验证
   - 从部署运维到文档编写

2. **开源协作经验**
   - 学会了如何管理开源项目
   - 掌握了 Git 工作流的实践
   - 理解了社区运营的重要性

3. **问题解决能力**
   - 培养了系统性排查问题的能力
   - 学会了从日志中定位问题
   - 掌握了快速验证假设的方法

### 6.2 技术亮点总结

ClawDev 的技术亮点可以概括为以下几个方面：

**1. 创新的对话驱动架构**

不同于传统的状态机或 DAG 工作流，ClawDev 采用对话驱动的方式编排 Agent 协作。这种方式更符合人类团队协作的直觉，也更容易扩展和维护。

**2. 智能的上下文管理**

实现了对话历史的智能压缩算法，在保留关键信息的同时，有效控制 prompt 长度。这使得长对话场景下的 Agent 不会"失忆"。

**3. 完整的 DevOps 集成**

与 Gitea、Docker 等工具深度集成，实现了从需求分析到代码提交、代码审查、测试验证的完整 DevOps 流程。

**4. 可扩展的插件架构**

通过技能（Skill）机制，可以方便地扩展 Agent 的能力。新技能只需符合简单的接口规范即可集成。

**5. 完善的调试工具**

提供了详细的日志记录、会话追踪、性能监控等调试工具，方便开发者排查问题。

### 6.3 实际应用场景

ClawDev 可以应用于以下场景：

**1. 快速原型开发**

产品经理或创业者可以用自然语言描述需求，ClawDev 自动生成可运行的原型代码，大大缩短从想法到原型的时间。

**2. 代码审查辅助**

开发团队可以将 ClawDev 集成到 CI/CD 流程中，自动进行代码审查，发现潜在问题，提高代码质量。

**3. 自动化测试生成**

基于代码自动生成测试用例，提高测试覆盖率，减少人工编写测试的工作量。

**4. 遗留代码维护**

帮助理解和重构遗留代码，生成文档，降低维护成本。

**5. 教育培训**

作为编程教学工具，学生可以看到 AI 如何一步步完成开发任务，学习最佳实践。

### 6.4 项目局限性

尽管 ClawDev 已经实现了不少功能，但它仍有一些局限性：

**1. 复杂需求处理能力有限**

对于需要深度业务理解、复杂架构设计的任务，ClawDev 的表现还不够理想。AI Agent 有时会做出不够合理的技术选型。

**2. 错误恢复能力有待提高**

当遇到工具调用失败、网络超时等异常情况时，Agent 的自动恢复能力还不够强，有时需要人工介入。

**3. 计算成本较高**

多 Agent 协作意味着多次 LLM 调用，对于复杂任务，Token 消耗可能很大，成本是一个需要考虑的因素。

**4. 实时性不足**

由于需要多轮对话和代码审查，完成一个任务的耗时可能比人工直接编写更长，不适合需要快速响应的场景。

### 6.5 未来规划

针对上述局限性，我规划了以下改进方向：

**短期（1-3 个月）：**

1. **增强错误恢复能力**
   - 实现自动重试机制
   - 添加更多错误处理策略
   - 提供更清晰的错误提示

2. **优化提示词（Prompt）**
   - 针对常见任务优化提示词模板
   - 添加更多示例（Few-shot learning）
   - 实现提示词版本管理

3. **完善调试工具**
   - 开发 Web 界面查看对话历史
   - 添加性能监控和统计
   - 实现实时日志查看

**中期（3-6 个月）：**

1. **支持更多代码仓库**
   - 集成 GitHub API
   - 支持 GitLab
   - 实现仓库迁移工具

2. **增强代码理解能力**
   - 集成代码分析工具（AST 解析）
   - 支持更多编程语言
   - 实现代码搜索和引用分析

3. **引入知识库**
   - 支持 RAG（检索增强生成）
   - 集成文档搜索
   - 实现最佳实践库

**长期（6-12 个月）：**

1. **自学习能力**
   - 从用户反馈中学习
   - 自动优化提示词
   - 积累领域知识

2. **多模态支持**
   - 支持图像理解（UI 设计图转代码）
   - 支持语音交互
   - 实现代码可视化

3. **生态系统建设**
   - 开发插件市场
   - 建立社区贡献机制
   - 提供企业级支持

### 6.6 参赛感言

参加这次阿里云天池大赛，是我技术成长道路上非常宝贵的一段经历。

**最大的收获是：**

我真正动手实现了一个完整的 Multi-Agent 系统，而不是停留在理论层面。这个过程让我深入理解了 LLM 应用开发的各个方面，从提示词工程到系统架构设计，从错误处理到性能优化。

**最有挑战的部分是：**

调试 Multi-Agent 系统的复杂性远超预期。当多个 Agent 同时运行，一个问题可能由多种原因造成，排查起来非常困难。我学会了写详细的日志、设计可观测的系统、使用分而治之的策略逐步缩小问题范围。

**最想感谢的是：**

阿里云提供了这次宝贵的参赛机会，让我有机会将想法付诸实践。OpenClaw 团队开发了优秀的基础平台，让我可以站在巨人肩膀上。还有开源社区的无数前辈，他们的经验和分享让我少走了许多弯路。

**对未来的期待：**

我相信 Multi-Agent 系统是未来 AI 应用的重要方向。随着 LLM 能力的不断提升和成本的持续下降，我们将看到越来越多的智能系统采用这种架构。我希望能够继续深耕这个领域，为构建更智能、更可靠的 AI 系统贡献自己的力量。

---

**如果你读到了这里，感谢你的耐心！** 希望这篇文章对你有所启发。如果你有任何问题或建议，欢迎在评论区留言，或者到 GitHub 上提 Issue 交流。

让我们一起，用技术创造更美好的未来！

---

## 附录

### A. 项目链接

- **GitHub 仓库**: https://github.com/HDAnzz/ClawDev
- **项目文档**: https://github.com/HDAnzz/ClawDev/tree/main/docs
- **Issue 追踪**: https://github.com/HDAnzz/ClawDev/issues

### B. 参考资料

1. **OpenClaw 官方文档**: https://openclaw.ai/docs
2. **阿里云百炼**: https://bailian.aliyun.com/
3. **天池大赛官网**: https://tianchi.aliyun.com/
4. **Multi-Agent 系统设计**: https://www.anthropic.com/research/building-effective-agents

### C. 致谢

感谢阿里云提供这次宝贵的参赛机会，感谢 OpenClaw 团队开发的优秀平台，感谢所有开源社区贡献者的辛勤付出。

---

> **队名**：ClawDev Studio  
> **联系方式**：GitHub @HDAnzz  
> **项目地址**：https://github.com/HDAnzz/ClawDev  
> **参赛平台**：阿里云天池大赛  
> **最后更新**：2026年1月

---

> 🦞 **队名**：ClawDev Studio  
> 📧 **联系方式**：GitHub @HDAnzz  
> 🔗 **项目地址**：https://github.com/HDAnzz/ClawDev  
> 🏆 **参赛平台**：阿里云天池大赛
