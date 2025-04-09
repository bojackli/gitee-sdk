# Gitee API SDK 设计文档

## 1. 项目概述

本项目旨在开发一个针对Gitee API的Python SDK，提供简洁、易用的接口，使开发者能够方便地与Gitee平台进行交互。SDK将覆盖Gitee提供的所有API功能，包括仓库管理、Issues、Pull Requests等。

## 2. 技术选择

- **编程语言**：Python 3.8+
- **依赖管理**：uv
- **HTTP客户端**：requests
- **测试框架**：pytest

## 3. 架构设计

### 3.1 整体架构

采用模块化设计，将SDK分为以下几个主要部分：

1. **核心模块**：处理认证、请求发送、响应解析等基础功能
2. **资源模块**：对应Gitee API的各个资源，如仓库、Issues、Pull Requests等
3. **异常处理**：统一的异常处理机制
4. **工具类**：提供辅助功能

### 3.2 目录结构

```
gitee-sdk/
├── .gitignore
├── LICENSE
├── README.md
├── DESIGN.md
├── pyproject.toml
├── docs/
│   └── ...
├── examples/
│   └── ...
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── ...
└── gitee/
    ├── __init__.py
    ├── client.py           # 主客户端类
    ├── auth.py             # 认证相关
    ├── config.py           # 配置相关
    ├── exceptions.py       # 异常定义
    ├── utils.py            # 工具函数
    └── resources/          # API资源模块
        ├── __init__.py
        ├── base.py         # 基础资源类
        ├── repositories.py # 仓库相关
        ├── issues.py       # Issues相关
        ├── pulls.py        # Pull Requests相关
        ├── users.py        # 用户相关
        ├── organizations.py # 组织相关
        ├── gists.py        # 代码片段相关
        ├── enterprises.py  # 企业相关
        ├── emails.py       # 邮箱相关
        ├── labels.py       # 标签相关
        ├── milestones.py   # 里程碑相关
        ├── webhooks.py     # 钩子相关
        ├── activities.py   # 动态通知相关
        ├── checks.py       # 门禁检查项相关
        ├── git_data.py     # 仓库数据相关
        ├── search.py       # 搜索相关
        └── misc.py         # 杂项
```

## 4. 核心组件设计

### 4.1 客户端（Client）

`Client` 类是SDK的主入口，负责初始化配置、认证和创建资源对象。

```python
class GiteeClient:
    def __init__(self, token=None, base_url="https://gitee.com/api/v5", timeout=10, **kwargs):
        self.base_url = base_url
        self.timeout = timeout
        self.auth = Auth(token) if token else None
        self.session = self._create_session(**kwargs)
        
        # 初始化各资源模块
        self.repositories = Repositories(self)
        self.issues = Issues(self)
        self.pulls = PullRequests(self)
        # ... 其他资源
    
    def _create_session(self, **kwargs):
        # 创建并配置HTTP会话
        pass
    
    def request(self, method, url, **kwargs):
        # 发送HTTP请求并处理响应
        pass
```

### 4.2 认证（Auth）

处理API认证相关的功能，支持多种认证方式。

```python
class Auth:
    def __init__(self, token=None, oauth_token=None):
        self.token = token
        self.oauth_token = oauth_token
    
    def apply_auth(self, headers):
        # 将认证信息应用到请求头
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        elif self.oauth_token:
            headers["Authorization"] = f"Bearer {self.oauth_token}"
        return headers
```

### 4.3 资源基类（Resource）

所有资源模块的基类，提供通用的请求方法。

```python
class Resource:
    def __init__(self, client):
        self.client = client
    
    def _get(self, url, **kwargs):
        return self.client.request("GET", url, **kwargs)
    
    def _post(self, url, **kwargs):
        return self.client.request("POST", url, **kwargs)
    
    def _put(self, url, **kwargs):
        return self.client.request("PUT", url, **kwargs)
    
    def _patch(self, url, **kwargs):
        return self.client.request("PATCH", url, **kwargs)
    
    def _delete(self, url, **kwargs):
        return self.client.request("DELETE", url, **kwargs)
```

### 4.4 异常处理

定义SDK特定的异常类，用于处理API错误和其他异常情况。

```python
class GiteeException(Exception):
    """基础异常类"""
    pass

class APIError(GiteeException):
    """API错误"""
    def __init__(self, status_code, error_code, message):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        super().__init__(f"[{status_code}] {error_code}: {message}")

class AuthenticationError(GiteeException):
    """认证错误"""
    pass

class RateLimitExceeded(GiteeException):
    """超出API速率限制"""
    pass
```

## 5. 资源模块设计 [TODO: 实现参数验证]

每个资源模块对应Gitee API的一个功能领域，封装相关的API调用。以下是几个主要资源模块的设计示例：

### 5.1 仓库（Repositories）

```python
class Repositories(Resource):
    """仓库相关API"""
    
    def list(self, visibility=None, affiliation=None, **kwargs):
        """获取仓库列表"""
        params = {}
        if visibility:
            params["visibility"] = visibility
        if affiliation:
            params["affiliation"] = affiliation
        params.update(kwargs)
        return self._get("/user/repos", params=params)
    
    def get(self, owner, repo):
        """获取仓库详情"""
        return self._get(f"/repos/{owner}/{repo}")
    
    def create(self, name, **kwargs):
        """创建仓库"""
        data = {"name": name}
        data.update(kwargs)
        return self._post("/user/repos", json=data)
    
    # ... 其他仓库相关方法
```

### 5.2 Issues

```python
class Issues(Resource):
    """Issues相关API"""
    
    def list(self, owner=None, repo=None, **kwargs):
        """获取Issues列表"""
        if owner and repo:
            url = f"/repos/{owner}/{repo}/issues"
        else:
            url = "/issues"
        return self._get(url, params=kwargs)
    
    def get(self, owner, repo, number):
        """获取Issue详情"""
        return self._get(f"/repos/{owner}/{repo}/issues/{number}")
    
    def create(self, owner, repo, title, **kwargs):
        """创建Issue"""
        data = {"title": title}
        data.update(kwargs)
        return self._post(f"/repos/{owner}/{repo}/issues", json=data)
    
    # ... 其他Issues相关方法
```

### 5.3 Pull Requests

```python
class PullRequests(Resource):
    """Pull Requests相关API"""
    
    def list(self, owner, repo, **kwargs):
        """获取Pull Requests列表"""
        return self._get(f"/repos/{owner}/{repo}/pulls", params=kwargs)
    
    def get(self, owner, repo, number):
        """获取Pull Request详情"""
        return self._get(f"/repos/{owner}/{repo}/pulls/{number}")
    
    def create(self, owner, repo, title, head, base, **kwargs):
        """创建Pull Request"""
        data = {
            "title": title,
            "head": head,
            "base": base
        }
        data.update(kwargs)
        return self._post(f"/repos/{owner}/{repo}/pulls", json=data)
    
    # ... 其他Pull Requests相关方法
```

## 6. 分页处理 [TODO: 实现完整的分页处理机制]

Gitee API返回的列表数据通常是分页的，SDK需要提供便捷的分页处理机制。

```python
class PaginatedList:
    """分页列表"""
    
    def __init__(self, client, url, params=None):
        self.client = client
        self.url = url
        self.params = params or {}
        self.current_page = 1
        self.per_page = min(params.get("per_page", 20), 100)  # 默认20条，最大100条
        self.total_pages = None
        self.total_count = None
        self.items = []
    
    def get_page(self, page=1, per_page=20):
        """获取指定页的数据"""
        params = self.params.copy()
        params.update({
            "page": page,
            "per_page": per_page
        })
        response = self.client.request("GET", self.url, params=params)
        self.current_page = page
        self.per_page = per_page
        # 从响应头中获取分页信息
        # ...
        return response
    
    def __iter__(self):
        """迭代所有页的数据"""
        page = 1
        while True:
            items = self.get_page(page)
            if not items:
                break
            for item in items:
                yield item
            page += 1
```

## 7. 错误处理策略 [TODO: 实现增强的日志记录功能]

SDK将采用以下错误处理策略：

1. **统一异常体系**：所有SDK异常继承自基础异常类`GiteeException`
2. **详细错误信息**：异常包含HTTP状态码、错误代码和错误消息
3. **重试机制**：对于可重试的错误（如网络超时、速率限制），提供自动重试功能
4. **日志记录**：记录请求和错误信息，便于调试

## 8. 依赖管理

使用uv进行依赖管理，在`pyproject.toml`中定义项目依赖：

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "gitee-sdk"
version = "0.1.0"
description = "Python SDK for Gitee API"
readme = "README.md"
requires-python = ">=3.8"
license = {file = "LICENSE"}
authors = [
    {name = "bojackli", email = "lovenpeace648@gmail.com"},
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
dependencies = [
    "httpx>=0.24.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.0.0",
    "mypy>=1.0.0",
]
docs = [
    "sphinx>=6.0.0",
    "sphinx-rtd-theme>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/bojackli/gitee-sdk"
Documentation = "https://gitee-sdk.readthedocs.io"
Issues = "https://github.com/bojackli/gitee-sdk/issues"

[tool.black]
line-length = 88
target-version = ["py38"]

[tool.isort]
profile = "black"

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
```

## 9. 使用示例

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

# 获取Pull Request
pr = client.pulls.get("octocat", "hello-world", 1)
print(f"PR #{pr['number']}: {pr['title']} ({pr['state']})")
```

## 10. 扩展性考虑

为确保SDK具有良好的扩展性，采取以下措施：

1. **模块化设计**：每个API资源独立封装，便于添加新功能
2. **配置灵活性**：允许用户自定义基础URL、超时设置等
3. **钩子机制**：提供请求前/后的钩子，允许用户自定义处理逻辑
4. **中间件支持**：支持添加请求/响应中间件，扩展功能
5. **版本兼容**：设计时考虑API版本变化，便于适配新版本

## 11. 后续开发计划

1. **完善文档**：编写详细的API文档和使用示例
2. **增加测试覆盖**：编写单元测试和集成测试
3. **CI/CD集成**：设置持续集成和部署流程
4. **性能优化**：优化请求处理和响应解析
5. **异步支持**：添加异步API支持
6. **类型提示**：完善类型注解，提高IDE支持
7. **命令行工具**：开发配套的命令行工具

