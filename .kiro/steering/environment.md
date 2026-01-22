# 环境配置

## 终端命令执行规则

用户安装了 Miniconda，终端默认会激活 conda base 环境。但项目使用的是系统 Python 环境。

**执行命令时必须先退出 conda 环境：**

```powershell
conda deactivate; <实际命令>
```

例如：
```powershell
conda deactivate; python tests/check_project.py
conda deactivate; python run_cli.py --select
conda deactivate; pip install xxx
```

## Python 环境

- 系统 Python: `C:\Users\17538\AppData\Local\Programs\Python\Python310\python.exe`
- 版本: Python 3.10.11
- 项目不使用 conda 环境
