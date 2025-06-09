Pipenv 虚拟环境管理指南

目录
# 安装与基础命令

# 虚拟环境位置

# 查看所有虚拟环境

# 包管理

# 环境配置

# 注意事项

安装与基础命令

安装pipenv

bash
pip install pipenv

基础命令
命令 描述

pipenv install 创建环境并安装依赖
pipenv --python 3.8 指定Python版本创建
pipenv shell 激活虚拟环境
exit 退出虚拟环境
pipenv --rm 删除当前虚拟环境

虚拟环境位置

默认存储路径
系统 路径

Linux/macOS ~/.local/share/virtualenvs/<项目名>-<随机字符串>
Windows %USERPROFILE%\.virtualenvs\<项目名>-<随机字符串>

包安装位置

<虚拟环境路径>/
├── bin/ (或 Scripts/)
├── lib/pythonX.X/site-packages/  # 实际安装位置
└── pyvenv.cfg

查看所有虚拟环境

方法1：直接查看目录

bash
Linux/macOS

ls ~/.local/share/virtualenvs/

Windows

dir %USERPROFILE%\.virtualenvs

方法2：使用find命令

bash
find ~/.local/share/virtualenvs/ -name "pyvenv.cfg" -exec dirname {} \;

方法3：安装pipenv-utils

bash
pip install pipenv-utils
pvenv list  # 列出所有环境

包管理

安装/卸载包
命令 描述

pipenv install requests 安装生产依赖
pipenv install pytest --dev 安装开发依赖
pipenv uninstall requests 卸载包
pipenv update 更新所有包

依赖管理

bash
pipenv lock  # 生成Pipfile.lock
pipenv sync  # 按Pipfile.lock精确安装
pipenv graph  # 查看依赖树

环境配置

修改默认位置

bash
在项目目录创建.venv

export PIPENV_VENV_IN_PROJECT=1  # Linux/macOS
set PIPENV_VENV_IN_PROJECT=1     # Windows

镜像源配置

在Pipfile中添加：
toml
[[source]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
verify_ssl = true
name = "pypi"

注意事项
不要手动修改虚拟环境目录，应使用pipenv命令管理

激活环境后可以用pip但不推荐，会跳过Pipfile更新

多项目共享包通过pipenv依赖解析优化实现

删除环境应使用pipenv --rm而非直接删除目录

提交项目时应包含Pipfile和Pipfile.lock

最佳实践

bash
新项目

mkdir project && cd project
pipenv --python 3.8
pipenv install requests pandas
pipenv install pytest --dev

日常开发

pipenv shell
编写代码...

exit

共享项目

pipenv lock
git add Pipfile Pipfile.lock
``
提示：使用pipenv-utils`工具可以更方便地管理多个虚拟环境
