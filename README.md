# REMADE.md

简洁说明项目的用途、快速上手与常用命令。

## 项目概述
本项目 blockchain-analyse：对加密市场数据进行指标计算与分析，包含对接交易所（例如 OKX/CCTX）、指标库与提示（prompt）服务等模块化实现。

## 目录（简要）
- src/api：HTTP 控制器与中间件
- src/core：全局配置与异常定义
- src/lib/indicators：指标实现与模型
- src/obj：数据对象、DTO 与分析结果
- src/service：分析、交易所适配与提示服务
- src/test：单元测试

## 环境要求
- Python 3.13.5
- virtualenv 已配置
- 已安装包示例：beautifulsoup4, click, numpy, pandas, protobuf, pytz, requests, six

## 快速上手
1. 克隆仓库并进入目录
2. 创建并激活虚拟环境
   - python -m virtualenv .venv
   - Linux/macOS: source .venv/bin/activate
   - Windows: .venv\Scripts\activate
3. 安装依赖
   - pip install -r requirements.txt
   （若无 requirements.txt，按需安装项目使用的包）

## 配置
- 复制环境示例：cp .env.example .env
- 在 .env 中填入 API 密钥、外部服务配置等

## 运行
- 本地运行（示例）
  - python main.py
- 如果项目提供 HTTP 服务，按控制器端点访问（查看 src/api/controller）

## 测试
- 运行所有测试：
  - pytest
- 单独运行某个测试文件：
  - pytest src/test/test_indicators.py

## 常用命令
- 格式化 / 静态检查（根据项目约定添加）
- 安装新包：
  - .venv/bin/pip install <package>
  - 或 Windows: .venv\Scripts\pip install <package>

## 开发注意点
- 使用 virtualenv 管理依赖，不使用其它包管理器（如 pipenv、poetry）除非另行说明。
- 配置敏感信息请放入 .env，切勿提交到 VCS。
- 新增模块后务必补充或更新单元测试。

## 贡献
欢迎提交 issue 和 PR；请描述复现步骤并包含测试用例（若适用）。

## 许可证
请参考仓库根目录的 LICENSE（若无则补充项目许可证信息）。