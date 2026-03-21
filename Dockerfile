# syntax=docker/dockerfile:1.7
# 基于 openclaw:local 扩展，新增 Homebrew、tea、QMD
# 构建命令：docker build -f Dockerfile.openclaw-custom -t openclaw:custom .

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

ENV HOMEBREW_BREW_GIT_REMOTE="https://mirrors.ustc.edu.cn/brew.git"
ENV HOMEBREW_CASK_GIT_REMOTE="https://mirrors.ustc.edu.cn/homebrew-cask.git"
RUN set -eux && \
    mkdir -p /home/linuxbrew/.linuxbrew && \
    chown -R node:node /home/linuxbrew && \
    \
    gosu node env \
      HOME=/home/node \
      NONINTERACTIVE=1 \
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" && \
    \
    gosu node env \
      HOME=/home/node \
      PATH="/home/linuxbrew/.linuxbrew/bin:$PATH" \
      brew update

RUN set -eux && \
    gosu node env \
      HOME=/home/node \
      PATH="/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:$PATH" \
      brew install tea

RUN set -eux && \
    gosu node env \
      HOME=/home/node \
      PATH="/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:$PATH" \
      brew install oven-sh/bun/bun && \
    gosu node sh -c "echo '[install]' > /home/node/.bunfig.toml && \
         echo 'registry = \"https://registry.npmmirror.com/\"' >> /home/node/.bunfig.toml"

ARG OPENCLAW_QMD_CUDA=false
ENV NODE_LLAMA_CPP_CUDA=${OPENCLAW_QMD_CUDA}
RUN set -eux && \
    npm config set registry https://registry.npmmirror.com && \
    npm install -g @tobilu/qmd

# ── 安装 uv ──────────────────────────────────────────────────────
RUN curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR=/usr/local/bin sh && \
    uv --version

ENV UV_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"

ENV PATH="${PATH}:/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:/home/node/.bun/bin"

USER node

RUN brew --version && tea --version && bun --version && qmd --version
