# 校园失物招领智能匹配平台

本项目是一个面向校园场景的失物招领管理系统，当前以 **Flask + MySQL** 实现基础业务流程，后续计划接入图片识别、文本向量检索与智能匹配能力。

当前仓库主要用于课程项目协作开发。代码仍在持续完善中，运行前请先阅读本文档中的环境配置、数据库初始化和已知限制。

## 1. 项目功能

当前基础功能包括：

- 用户注册、登录和退出
- 发布失物或拾获物品
- 按名称、描述和分类查询物品
- 查看物品详情
- 编辑和删除本人发布的物品
- 查看和修改个人资料
- 管理员查看用户、物品和分类
- 管理员删除物品、删除用户及切换管理员权限
- 通知列表页面

后续计划完善：

- 全站中文文案与页面样式统一
- 认领申请和通知生成流程
- 邮件验证码与密码找回配置
- 图片内容识别与标签提取
- 文本向量检索与失物智能匹配
- 数据库配置环境变量化

## 2. 技术栈

- Python 3.10
- Flask 3.0
- Flask-SQLAlchemy
- Flask-Login
- Flask-Bcrypt
- Flask-Mail
- MySQL 8.0
- PyMySQL
- Jinja2
- Bootstrap

推荐使用 **Python 3.10**。当前依赖文件中包含部分 Windows 相关包，不建议直接使用 Python 3.13 运行本项目。

## 3. 项目结构

```text
lost-found-management/
├── app.py                 # Flask 应用入口和主要路由
├── models.py              # SQLAlchemy 数据模型
├── init_db.py             # 根据 models.py 创建数据表
├── dbs.sql                # 旧版数据库脚本，仅供参考
├── requirements.txt       # Python 依赖
├── templates/             # Jinja2 页面模板
├── static/                # CSS、图片等静态资源
└── README.md              # 项目说明
```

数据库表结构以 `models.py` 和 `init_db.py` 为准。

`dbs.sql` 中部分字段和当前模型不完全一致，并存在重复外键语句，因此不建议直接导入该文件初始化数据库。

## 4. 获取代码

```bash
git clone https://github.com/hanheehhe/lost-found-management.git
cd lost-found-management
```

团队成员开发新功能时，请从最新的 `main` 分支创建独立分支，不要直接修改 `main`：

```bash
git switch main
git pull
git switch -c feature/功能名称
```

## 5. 创建 Python 环境

### 5.1 使用 Conda

```bash
conda create -n lostfound-py310 python=3.10 -y
conda activate lostfound-py310
python --version
```

确认输出为 Python 3.10.x 后安装依赖：

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5.2 使用 Python venv

创建虚拟环境：

```bash
python -m venv .venv
```

PowerShell 激活环境：

```powershell
.venv\Scripts\Activate.ps1
```

CMD 激活环境：

```cmd
.venv\Scripts\activate
```

安装依赖：

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5.3 PyCharm 配置

1. 使用 PyCharm 打开项目根目录。
2. 打开 `Settings`。
3. 进入 `Project → Python Interpreter`。
4. 选择已有的 Python 3.10 环境，或新建 Python 3.10 虚拟环境。
5. 在 PyCharm Terminal 中执行：

```bash
pip install -r requirements.txt
```

### 5.4 VS Code 配置

1. 使用 VS Code 打开项目根目录。
2. 按 `Ctrl+Shift+P`。
3. 选择 `Python: Select Interpreter`。
4. 选择刚创建的 Python 3.10 环境。
5. 在终端中确认：

```bash
python --version
```

## 6. 准备 MySQL 数据库

项目当前默认数据库名称为：

```text
lost-found_db
```

当前 `app.py` 中的默认连接配置为：

```python
mysql+pymysql://root:123456@localhost/lost-found_db?charset=utf8mb4
```

这仍是临时开发配置。数据库地址、账号和密码后续会改为通过环境变量读取。

个人本机的数据库密码、地址或驱动修改不得提交到 Git 仓库。

### 6.1 方式一：使用本机 MySQL

确认 MySQL 8.0 已启动，然后通过 SQLyog、MySQL Workbench 或 MySQL 命令行执行：

```sql
CREATE DATABASE IF NOT EXISTS `lost-found_db`
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

当前代码默认使用以下连接信息：

```text
主机：localhost
端口：3306
用户名：root
密码：123456
数据库：lost-found_db
```

SQLyog 只是 MySQL 的可视化管理工具，不负责运行 Python 项目。

### 6.2 方式二：使用 Docker MySQL

确保 Docker Desktop 已启动，然后在 PowerShell 中执行：

```powershell
docker run --name lostfound-mysql -e MYSQL_ROOT_PASSWORD=123456 -e MYSQL_DATABASE=lost-found_db -p 3306:3306 -d mysql:8.0
```

查看容器状态：

```powershell
docker ps
```

查看 MySQL 启动日志：

```powershell
docker logs lostfound-mysql
```

后续再次使用已有容器时：

```powershell
docker start lostfound-mysql
```

停止容器：

```powershell
docker stop lostfound-mysql
```

`123456` 仅用于当前本地开发环境，不得用于正式部署。

## 7. 创建数据库表

`init_db.py` 只负责创建数据表，不会自动创建 MySQL 数据库。

确认以下条件已经满足：

- MySQL 已启动
- `lost-found_db` 数据库已创建
- `app.py` 中的连接信息与本机环境一致
- Python 环境已激活
- 依赖已安装

然后执行：

```bash
python init_db.py
```

成功时会显示：

```text
数据库表创建成功
```

## 8. 初始化基础分类

`init_db.py` 不会自动添加物品分类。分类表为空时，发布页面可能无法正常选择分类。

可以通过 SQLyog、MySQL Workbench 或 MySQL 命令行执行：

```sql
USE `lost-found_db`;

INSERT IGNORE INTO categories (name) VALUES
('证件卡类'),
('电子产品'),
('书籍资料'),
('衣物饰品'),
('生活用品'),
('其他');
```

分类名称可以由团队根据最终需求统一调整。

## 9. 创建管理员账号

项目目前不会自动生成管理员账号。

先通过网页注册一个普通用户，然后在数据库中执行：

```sql
USE `lost-found_db`;

UPDATE users
SET is_admin = 1
WHERE email = '需要设为管理员的邮箱';
```

重新登录后即可访问管理员页面。

## 10. 默认图片

物品和用户模型默认使用：

```text
static/images/default.jpg
```

当前仓库可能未包含该文件。运行项目前请确认该路径存在，并放入一张名为 `default.jpg` 的占位图片，否则部分页面可能出现图片加载失败。

## 11. 启动项目

启动前确认：

- Python 3.10 环境已激活
- Python 依赖已安装
- MySQL 已启动
- 数据库已创建
- 数据表已初始化
- 分类数据已添加

执行：

```bash
python app.py
```

浏览器访问：

```text
http://127.0.0.1:5000
```

## 12. 建议测试流程

首次运行后建议按以下顺序测试：

1. 打开首页。
2. 注册普通用户并登录。
3. 发布一条失物或拾获信息。
4. 查看物品详情。
5. 编辑本人发布的物品。
6. 删除本人发布的物品。
7. 查看并修改个人资料。
8. 查看通知页面。
9. 使用管理员账号进入后台。
10. 创建两个普通用户，确认用户不能编辑或删除他人发布的物品。

## 13. 常见问题

### 13.1 `ModuleNotFoundError`

确认当前终端使用的是正确的 Python 环境：

```bash
python --version
pip --version
```

然后重新安装依赖：

```bash
pip install -r requirements.txt
```

### 13.2 无法连接 MySQL

检查 MySQL 或 Docker 容器是否已启动：

```powershell
docker ps
```

检查以下内容是否与 `app.py` 一致：

- 主机地址
- 端口
- 数据库名称
- 用户名
- 密码
- SQLAlchemy 数据库驱动

部分 Windows 环境中，`localhost` 可能连接异常。可以仅在本机调试时临时改为：

```text
127.0.0.1
```

该修改属于个人环境配置，不要提交到团队仓库。

### 13.3 `Unknown database 'lost-found_db'`

说明数据库尚未创建。执行：

```sql
CREATE DATABASE IF NOT EXISTS `lost-found_db`
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

然后重新执行：

```bash
python init_db.py
```

### 13.4 发布页面没有分类

说明 `categories` 表中没有数据。执行本文档“初始化基础分类”一节中的 SQL。

### 13.5 Docker 提示 3306 端口被占用

本机 MySQL 和 Docker MySQL 不能同时占用 3306 端口。

可选择其中一种处理方式：

- 停止本机 MySQL，再启动 Docker 容器
- 不使用 Docker，直接连接本机 MySQL
- 修改 Docker 端口映射，并同步调整本机数据库连接配置

### 13.6 `localhost` 可连接，但 PyMySQL 驱动报错

项目默认驱动为：

```text
mysql+pymysql
```

对应依赖为：

```text
PyMySQL
```

请先确认 PyMySQL 已安装：

```bash
pip show PyMySQL
```

不要为了个人环境随意把数据库驱动修改提交到团队仓库。驱动切换应由团队统一决定。

### 13.7 默认图片无法显示

检查以下文件是否存在：

```text
static/images/default.jpg
```

### 13.8 密码找回邮件无法发送

当前邮件账号和密码仍是占位配置，因此密码找回邮件默认无法正常发送。

在团队完成 SMTP 配置前，邮件发送失败不代表 Flask 或数据库启动失败。

### 13.9 页面存在中英文混杂

当前页面文案和样式仍在统一过程中，不影响基础后端功能运行。前端负责人后续会单独整理页面文字和视觉样式。

## 14. 协作规范

- 不直接在 `main` 分支开发。
- 每项功能、修复或文档修改使用独立分支。
- 开发前先同步最新 `main`。
- 提交前完成本地测试。
- 不提交个人数据库密码、邮箱密码、Token 或绝对本机路径。
- 不提交虚拟环境目录和 IDE 本地配置。
- 不把无关修改放入同一个 PR。
- 创建 PR 后等待代码 review，再合并到 `main`。

推荐分支命名：

```text
feature/功能名称
fix/问题名称
docs/文档名称
refactor/重构内容
```

推荐提交信息：

```text
feat: 增加智能匹配功能
fix: 修复物品编辑权限问题
docs: 补充项目运行说明
refactor: 整理数据库配置
```

## 15. 当前已知限制

项目目前仍处于课程开发阶段，以下内容尚未全部完成：

- 数据库连接仍为临时硬编码
- SMTP 邮件服务尚未正式配置
- 认领与通知生成流程仍需完善
- 前端中文文案和样式仍需统一
- `requirements.txt` 仍需精简
- `dbs.sql` 与当前模型需要重新整理
- 默认占位图片需要补充
- AI 图片识别与语义匹配尚未接入

开始开发新功能前，请先同步最新 `main`，并确认注册、登录、发布、编辑、删除和管理员功能仍能正常运行。
