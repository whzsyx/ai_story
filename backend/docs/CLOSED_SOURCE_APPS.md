# 闭源模块发布说明

`backend/apps/agent` 和 `backend/apps/mcp` 采用“源码在私有仓库开发、开源仓库只保留编译产物”的模式。

## 本地开发

1. 将闭源源码放到单独私有 Git 仓库，并保持与主仓库一致的包结构：`backend/apps/agent`、`backend/apps/mcp`。
2. 在本地环境设置 `PRIVATE_BACKEND_APPS_ROOT=/absolute/path/to/private_repo/backend/apps`。
3. Django 导入 `apps.agent`、`apps.mcp` 时，会优先从 `PRIVATE_BACKEND_APPS_ROOT` 加载源码；未配置时，再回退到当前仓库内的编译产物。

## 发布约束

1. 开源仓库中的 `backend/apps/agent`、`backend/apps/mcp` 目录只允许保留 `.so` 文件。
2. 不要将 `.py`、`.pyi`、测试、文档、源码生成脚本提交到上述目录。
3. 构建完成后，仅同步编译产物到开源仓库，再执行检查脚本。

## 检查命令

```bash
bash scripts/check_closed_source_apps.sh
```

检查脚本会扫描以下目录并在发现非 `.so` 文件时返回非零退出码：

- `backend/apps/agent`
- `backend/apps/mcp`

## 注意事项

- `.gitignore` 只负责忽略未跟踪文件，已经被 Git 跟踪的源码仍需迁移出仓库历史或手动删除后再提交。
- 私有仓库建议保持与主仓库相同的 Python 包名，避免改动 Django `INSTALLED_APPS`、路由和导入路径。
