#!/bin/bash
# 检查Python版本是否符合要求(>=3.8)
PYTHON_VERSION=$(python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
if [[ "$(printf '%s\n' '3.8' "$PYTHON_VERSION" | sort -V | head -n1)" != "3.8" ]]; then
    echo "错误: 需要Python 3.8或更高版本，当前版本为$PYTHON_VERSION"
    echo "建议使用pyenv或conda安装Python 3.8+版本"
    exit 1
fi

# 如果没有uv环境，请先执行以下命令安装
# python -m pip install uv

# 创建Python虚拟环境
python -m venv gitee-sdk

# 激活虚拟环境
source gitee-sdk/bin/activate

# 安装项目依赖
uv pip install -e ".[dev]"
uv pip install requests
uv pip install pytest pytest-cov

# 打印完成信息
echo "环境设置完成，请运行'source gitee-sdk/bin/activate'激活虚拟环境"