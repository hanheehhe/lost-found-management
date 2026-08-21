本项目是一个面向校园场景的失物招领管理系统，当前以 **Flask + MySQL** 实现基础业务流程，后续计划接入图片识别、文本向量检索与智能匹配能力。

当前仓库主要用于课程项目协作开发。代码仍在持续完善中，运行前请先阅读本文档中的环境配置、数据库初始化和已知限制。
## 1. 项目功能
一 用户功能
用户注册
用户填写基本信息完成注册
注册信息保存至 MySQL 数据库
支持账号登录验证

用户登录与退出
用户通过账号密码登录系统
使用 Flask-Login 实现用户状态管理
支持安全退出登录

密码管理
提供忘记密码页面
支持密码重置功能
后续可接入邮箱验证码验证

个人中心
用户可以：
查看个人信息
修改用户名、邮箱等资料
修改个人头像
查看自己发布的物品信息

后续计划完善：

- 全站中文文案与页面样式统一
- 认领申请和通知生成流程
- 邮件验证码与密码找回配置
- 数据库配置环境变量化

二 失物招领业务功能
1. 发布物品信息

用户可以发布：

丢失物品
拾获物品

填写内容包括：

物品名称
物品分类
详细描述
丢失/拾获地点
图片信息
发布时间
2. 物品查询

系统支持：

按物品名称搜索
按描述关键词搜索
按分类筛选

方便用户快速查找相关物品。

3. 查看物品详情

用户可以查看：

物品图片
物品名称
分类
描述信息
发布用户
发布时间
4. 物品管理

用户只能管理自己发布的信息：

包括：

编辑物品
删除物品

系统通过权限控制避免用户修改或删除其他用户的数据。

三、管理员功能

管理员拥有系统管理权限。

1. 用户管理

管理员可以：

查看所有用户
删除用户
修改用户管理员权限
2. 物品管理

管理员可以：

查看全部失物信息
删除违规或错误发布的信息
3. 分类管理

管理员可以：

查看物品分类
管理分类数据
4. 后台管理页面

管理员通过后台页面统一管理系统数据。

四、通知功能

系统提供通知页面，用于展示：

系统消息
后续认领申请通知
匹配结果提醒

当前通知模块已完成基础页面，后续继续完善自动生成逻辑。
## 2. 技术栈

后端
Python 3.10
Flask 3.0
Flask-SQLAlchemy
Flask-Login
Flask-Bcrypt
Flask-Mail
数据库
MySQL 8.0
PyMySQL
前端
HTML
CSS
JavaScript
Bootstrap
Jinja2模板
推荐使用 **Python 3.10**。当前依赖文件中包含部分 Windows 相关包，不建议直接使用 Python 3.13 运行本项目。

## 3. 项目结构
lost-found-management/

├── app.py              # Flask程序入口及路由
├── models.py           # 数据库模型
├── init_db.py          # 数据库表初始化
├── requirements.txt    # Python依赖
│
├── templates/          # HTML页面模板
│
├── static/
│   ├── css/            # 样式文件
│   ├── js/             # JavaScript文件
│   └── images/         # 图片资源
│
└── README.md
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

## 5. 开发环境配置

推荐开发环境：

Windows 10/11
Python 3.10
PyCharm
MySQL 8.0
SQLyog
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

### 6.2 方式二：使用 Docker MySQL（不推荐）

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

## 13. AI 智能匹配使用说明

### 13.1 功能简介

系统集成阿里云百炼 DashScope 两个模型，实现失物招领的智能查找：

- 视觉理解模型：发布物品时自动识别图片中的类别、颜色、材质、品牌、显著特征。
- 多模态向量匹配：为物品生成向量，查找时按相似度返回最接近的结果。

### 13.2 前置准备

1. 配置 API Key：在项目根目录的 `.env` 文件中填入阿里云百炼 DashScope 的 Key（`.env` 已被 gitignore 忽略，不会提交）：

```text
DASHSCOPE_API_KEY=sk-你的阿里云Key
```

没有 `.env` 文件时，可复制 `.env.example` 改名后填入。

2. 安装依赖：`requirements.txt` 中已包含 `dashscope`，正常 `pip install -r requirements.txt` 即可。

未配置 API Key 时，AI 功能会自动跳过，不影响物品的正常发布与浏览。

### 13.3 发布物品时自动识别

发布物品（丢失/拾获）时上传图片，系统会自动调用视觉理解模型提取结构化标签（类别、颜色、材质、品牌、特征），并把匹配向量存入数据库。

- 识别成功时，发布页会提示「发布成功，AI 已自动识别特征」。
- 编辑物品并更换图片后，会重新识别并更新向量。

### 13.4 AI 智能匹配查找

1. 登录后点击导航栏的「AI 智能匹配」。
2. 选择查找方向：
   - 拾获物品（找失物）
   - 遗失物品（找拾获）
   - 不限
3. 输入文字描述，或上传图片（两者可同时提供）。
4. 点击「开始匹配」，系统按相似度从高到低返回 Top 10 结果，并显示每条结果的相似度百分比。
5. 点击「查看详情」跳转到物品详情页。

### 13.5 无 Key 时的降级行为

未配置 API Key 或调用失败时，AI 匹配会退化为关键词搜索：仅按文字对物品名称、描述做模糊匹配，并提示「AI 未启用，已退化为关键词搜索」。

## 14. 协作规范

不提交 .venv 虚拟环境
不提交个人数据库密码
不提交个人邮箱密码
不提交 IDE 配置文件
修改代码前同步最新 main 分支
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
当前开发计划
已完成

√ 用户注册登录
√ 用户权限控制
√ 发布失物信息
√ 发布拾获信息
√ 物品搜索
√ 分类筛选
√ 物品详情查看
√ 个人资料修改
√ 用户物品管理
√ 管理员后台管理
√ 通知页面
√ AI 智能匹配

后续开发
前端优化
页面中文化
页面布局优化
UI风格统一
系统功能完善
认领申请流程
自动通知生成
邮箱验证码
找回密码完善

开始开发新功能前，请先同步最新 `main`，并确认注册、登录、发布、编辑、删除和管理员功能仍能正常运行。
