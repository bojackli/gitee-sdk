# Gitee SDK

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

一个功能完整、结构清晰、易于使用的Gitee API Python SDK，使用uv进行依赖管理。

## 功能特点

- 完整覆盖Gitee API的所有功能
- 模块化设计，结构清晰
- 简洁易用的接口
- 完善的错误处理
- 支持分页处理
- 类型提示，提高IDE支持
- 详细的文档和示例

## 安装

```bash
pip install gitee-sdk
```

使用uv安装：

```bash
uv pip install gitee-sdk
```

## 快速开始

```python
from gitee import GiteeClient

# 创建客户端
client = GiteeClient(token="your_access_token")

# 获取用户仓库列表
repos = client.repositories.list()
for repo in repos:
    print(f"{repo['full_name']}: {repo['description']}")

# 创建Issue
issue = client.issues.create(
    owner="octocat",
    repo="hello-world",
    title="Found a bug",
    body="I'm having a problem with this."
)
print(f"Created issue #{issue['number']}: {issue['title']}")
```

## 支持的API

- 仓库管理 (Repositories)
- Issues管理
- Pull Requests
- 用户管理 (Users)
- 组织管理 (Organizations)
- 代码片段 (Gists)
- 企业管理 (Enterprises)
- 邮箱管理 (Emails)
- 标签管理 (Labels)
- 里程碑管理 (Milestones)
- Webhooks
- 动态通知 (Activities)
- 门禁检查项 (Checks)
- 仓库数据 (Git Data)
- 搜索 (Search)
- 杂项 (Miscellaneous)

## 详细文档

查看[设计文档](DESIGN.md)了解更多关于SDK架构和设计的信息。

## 开发

### 环境设置

```bash
# 克隆仓库
git clone https://github.com/bojackli/gitee-sdk.git
cd gitee-sdk

# 使用uv安装依赖
uv pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

## 贡献

欢迎贡献代码、报告问题或提出改进建议！

## 许可证

[MIT](LICENSE)