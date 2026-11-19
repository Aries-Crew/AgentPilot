# AgentPilot

AI agent 自我改進框架——用策略模型指導大模型做更好的決策。

## 結構

三個子套件，各有獨立的 `pyproject.toml`：

| 套件 | 路徑 | 用途 |
|------|------|------|
| agentpilot | `agentpilot/` | 核心：策略學習（UCB + Memory-based） |
| rsi-arena | `arena/` | 評估：RSI 競技場與 benchmark |
| openspace | `openspace/` | 技能管理與演化 |

## 開發

```bash
# 跑測試（需 Python ≥3.11）
uv run --python 3.12 pytest tests/ -v

# Lint
uv run --python 3.12 ruff check agentpilot/src/ --config agentpilot/pyproject.toml

# Type check（目前只 check domain 層）
uv run --python 3.12 mypy agentpilot/src/agentpilot/domain/ --config-file agentpilot/pyproject.toml
```

## 慣例

- 測試在 `tests/`，按子套件分子目錄
- domain 層用 frozen dataclass + `require_text` / `require_aware` 邊界驗證
- CI 由 GitHub Actions 在 PR 與 push to main 時觸發
