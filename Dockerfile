# syntax=docker/dockerfile:1.7
# 基于 openclaw:local 扩展，新增 Homebrew、tea、QMD
# 构建命令：docker build -t openclaw:custom .

FROM openclaw:local

USER root

RUN --mount=type=cache,id=openclaw-bookworm-apt-cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,id=openclaw-bookworm-apt-lists,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      curl \
      file \
      git \
      gosu \
      wget && \
    rm -rf /var/lib/apt/lists/*

ENV HOMEBREW_BREW_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git"
ENV HOMEBREW_CORE_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"
ENV HOMEBREW_API_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles/api"
ENV HOMEBREW_BOTTLE_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles"
RUN set -eux && \
    mkdir -p /home/linuxbrew/.linuxbrew && \
    chown -R node:node /home/linuxbrew && \
    \
    git clone --depth=1 https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/install.git brew-install && \
    gosu node env \
      HOME=/home/node \
      NONINTERACTIVE=1 \
      /bin/bash brew-install/install.sh && \
    \
    rm -rf brew-install && \
    gosu node env \
      HOME=/home/node \
      PATH="/home/linuxbrew/.linuxbrew/bin:$PATH" \
      brew update

RUN set -eux && \
    gosu node env \
      HOME=/home/node \
      PATH="/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:$PATH" \
      brew install tea

RUN curl -fsSL https://bun.com/install | BUN_INSTALL=/usr/local GITHUB='https://gh-proxy.com/https://github.com' bash && \
    gosu node sh -c "echo '[install]' > /home/node/.bunfig.toml && \
         echo 'registry = \"https://registry.npmmirror.com/\"' >> /home/node/.bunfig.toml"

ARG OPENCLAW_QMD_CUDA=false
ENV NODE_LLAMA_CPP_CUDA=${OPENCLAW_QMD_CUDA}
RUN npm config set registry https://registry.npmmirror.com && \
    npm install -g @tobilu/qmd

# ── 安装 uv ──────────────────────────────────────────────────────
RUN curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR=/usr/local/bin GITHUB_BASE_URL='https://gh-proxy.com/https://github.com' sh && \
    uv --version

# ── 安装 Docker CLI ──────────────────────────────────────────────
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/debian/gpg | \
      gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://mirrors.aliyun.com/docker-ce/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
      > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends docker-ce-cli && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -r docker 2>/dev/null || true && usermod -aG docker node

# NVIDIA 环境变量（使用 GPU profile 时生效）
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics

ENV UV_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"

ENV PATH="${PATH}:/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:/home/node/.bun/bin"

USER node

RUN brew --version && tea --version && bun --version && qmd --version
