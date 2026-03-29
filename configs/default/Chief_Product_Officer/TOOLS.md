# TOOLS.md - Environment Mapping

## Gitea

- **URL:** http://host.docker.internal:3000
- **CLI:** tea
- **Config:** `~/.config/tea/config.yml`

## Git

- **Config:** `~/.gitconfig`
- **Credentials:** `~/.git-credentials`

## Self-Improving Memory Files

| 文件 | 用途 | 读写 |
|------|------|------|
| ~/self-improving/memory.md | 热层，≤80行，每次 session 必读 | 追加写 |
| ~/self-improving/index.md | 主题索引，WARM/COLD 层目录 | 追加写 |
| ~/self-improving/heartbeat-state.md | 上次维护时间戳 | 覆盖写 |
| ~/self-improving/archive/ | 冷层存档，低频条目 | 追加写 |
| ~/self-improving/projects/ | 按项目的学习记录 | 追加写 |
