# DocuBot - Troubleshooting Guide

## Quick Fix: "streamlit is not recognized"

### 问题
```
'streamlit' 不是内部或外部命令，也不是可运行的程序或批处理文件。
(or on Mac/Linux: command not found: streamlit)
```

### 原因
Virtual environment 没有被正确激活，或 streamlit 没有安装

### ✅ 解决方案

#### Option 1: 使用改进的启动脚本 (推荐)

**Windows:**
```bash
# 方式 1A: 双击此文件
run_streamlit.bat

# 方式 1B: 或在 PowerShell 中运行
.\run_streamlit.ps1
```

**Mac/Linux:**
```bash
# 先给脚本执行权限
chmod +x run_streamlit.sh

# 然后运行
./run_streamlit.sh
```

#### Option 2: 手动安装和运行

**Windows (PowerShell):**
```powershell
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 安装 streamlit
pip install streamlit

# 运行应用
python -m streamlit run app.py
```

**Mac/Linux (Terminal):**
```bash
# 激活虚拟环境
source venv/bin/activate

# 安装 streamlit
pip install streamlit

# 运行应用
python -m streamlit run app.py
```

#### Option 3: 完整重新安装

如果上面都不行，尝试完整重装：

```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# 然后运行
python -m streamlit run app.py
```

```bash
# Mac/Linux
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 然后运行
python -m streamlit run app.py
```

---

## 其他常见问题

### Problem 1: Port 8501 already in use

**症状:**
```
ERROR in _on_request
ConnectionRefusedError: [Errno 10061] 连接被拒绝
(or: Address already in use)
```

**原因:** 另一个 Streamlit 实例已在运行

**解决:**

**Windows:**
```powershell
# 找出占用 8501 的进程
netstat -ano | findstr :8501

# 或使用 Streamlit 的不同端口
python -m streamlit run app.py --server.port 8502
```

**Mac/Linux:**
```bash
# 找出占用 8501 的进程
lsof -i :8501

# 或使用不同端口
python -m streamlit run app.py --server.port 8502
```

---

### Problem 2: "docs_pt/ folder not found"

**症状:** 侧栏显示黄色警告

**原因:** 知识库文档还没有准备

**解决:**
```bash
# 激活虚拟环境后运行：
python prepare_docs.py

# 然后重启 Streamlit
```

---

### Problem 3: "LLM is unavailable"

**症状:** 黄色警告 "LLM is unavailable. Using Retrieval Only mode."

**原因:** GEMINI_API_KEY 未设置

**解决:**

1. 编辑 `.env` 文件（项目根目录）
2. 添加你的 API 密钥：
   ```
   GEMINI_API_KEY=your_actual_key_here
   ```
3. 保存文件
4. 重启 Streamlit

**临时方案:** 继续用 Retrieval Only 模式（不需要 API）

---

### Problem 4: ModuleNotFoundError: No module named 'nltk'

**症状:**
```
ModuleNotFoundError: No module named 'nltk'
```

**原因:** nltk 包没有安装

**解决:**
```bash
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1  (Windows)
source venv/bin/activate       (Mac/Linux)

# 安装缺失的包
pip install nltk google-genai python-dotenv python-docx pdfplumber
```

---

### Problem 5: White screen / App crashes

**症状:** Streamlit 打开但是白屏，或者直接崩溃

**原因:** Python 代码有错误或依赖问题

**解决步骤:**

1. **查看 Terminal 的错误信息** (很重要！)
2. **停止 Streamlit:**
   ```
   按 Ctrl+C 在 Terminal 中
   ```

3. **检查语法:**
   ```bash
   python -m py_compile app.py
   ```

4. **重新安装所有依赖:**
   ```bash
   pip install -r requirements.txt
   ```

5. **启用更详细的日志:**
   ```bash
   python -m streamlit run app.py --logger.level=debug
   ```

6. **查看错误信息，根据具体错误修复**

---

### Problem 6: "No documents found in docs_pt/"

**症状:** 侧栏显示 "No documents found"

**原因:** 文件夹为空或不存在

**解决:**

**方式 1: 从 Word/PDF 生成**
```bash
# 确保你有原始文件
# 然后运行转换脚本
python prepare_docs.py
```

**方式 2: 手动添加 Markdown 文件**
```bash
# 创建 docs_pt 文件夹
mkdir docs_pt

# 把你的 .md 文件放进去
# 重启 Streamlit
```

**方式 3: 检查路径**
```bash
# 确保你在正确的目录
cd "D:\CodePath\Final Project\ai110-module4tinker-docubot-starter"

# 验证文件夹存在
ls docs_pt/
```

---

### Problem 7: "Cannot connect to http://localhost:8501"

**症状:** 浏览器打不开应用

**原因:** 服务器没启动成功，或浏览器问题

**解决:**

1. **检查 Terminal 是否显示:**
   ```
   Uvicorn server started on :::8501
   ```

2. **如果没有，看上面的错误信息，修复错误**

3. **试试直接访问:**
   - 浏览器手动输入: `http://localhost:8501`
   - 或: `http://127.0.0.1:8501`
   - 或网络地址: `http://192.168.x.x:8501`

4. **试试其他浏览器** (Chrome, Firefox, Safari)

5. **重启 Streamlit:**
   ```bash
   按 Ctrl+C 停止
   再运行一次
   ```

---

## 调试技巧

### 启用详细日志

```bash
# 调试级别
python -m streamlit run app.py --logger.level=debug

# 信息级别
python -m streamlit run app.py --logger.level=info

# 减少日志（默认）
python -m streamlit run app.py --logger.level=warning
```

### 检查日志文件

应用运行时会生成日志文件：
- `guardrail_blocks.jsonl` - 被拦截的查询
- `retrieval_results.jsonl` - 检索结果
- `user_feedback.jsonl` - 用户反馈

**查看日志:**
```bash
# Windows
type guardrail_blocks.jsonl

# Mac/Linux
cat guardrail_blocks.jsonl

# 或用任何文本编辑器打开
```

### 测试各个组件

```bash
# 测试检索
python -c "from docubot import DocuBot; bot = DocuBot(); print('✓ Retrieval OK')"

# 测试 LLM
python -c "from llm_client import GeminiClient; c = GeminiClient(); print('✓ LLM OK')"

# 测试防护
python -c "from guardrail import check_input_safety; print(check_input_safety('test'))"

# 测试日志
python -c "from logger import get_logger; logger = get_logger(); print('✓ Logger OK')"
```

---

## 完整重置

如果一切都不行，尝试完整重置：

**Windows:**
```powershell
# 1. 删除虚拟环境（可选）
Remove-Item -Recurse -Force .\.venv

# 2. 删除日志文件（可选）
Remove-Item *.jsonl

# 3. 重新创建虚拟环境
python -m venv .venv

# 4. 激活
.\.venv\Scripts\Activate.ps1

# 5. 安装依赖
pip install -r requirements.txt

# 6. 运行
python -m streamlit run app.py
```

**Mac/Linux:**
```bash
# 1. 删除虚拟环境
rm -rf venv

# 2. 删除日志文件
rm *.jsonl

# 3. 重新创建
python3 -m venv venv

# 4. 激活
source venv/bin/activate

# 5. 安装依赖
pip install -r requirements.txt

# 6. 运行
python -m streamlit run app.py
```

---

## 获取帮助

如果还是无法解决，请收集以下信息：

```bash
# 1. Python 版本
python --version

# 2. 虚拟环境中的包
pip list

# 3. 错误信息的完整文本（从 Terminal）

# 4. 操作系统信息
# Windows: winver
# Mac: system_profiler SPSoftwareDataType
# Linux: uname -a
```

然后查看：
- `STEP3_SUMMARY.md` - 技术细节
- `STREAMLIT_UI_GUIDE.md` - UI 文档
- `QUICKSTART_UI.md` - 快速指南

或在项目代码中查找相关注释。

---

## 常用命令速查表

```bash
# 激活虚拟环境
Windows:    .\.venv\Scripts\Activate.ps1
Mac/Linux:  source venv/bin/activate

# 运行 Streamlit
python -m streamlit run app.py

# 运行其他脚本
python verify_step3_critical.py    # 验证系统
python step3_evaluation.py          # 完整测试
python prepare_docs.py              # 准备文档

# 检查日志
type guardrail_blocks.jsonl         # Windows
cat guardrail_blocks.jsonl          # Mac/Linux

# 停止服务
Ctrl+C (在 Terminal)

# 使用不同端口
python -m streamlit run app.py --server.port 8502
```

---

**还是有问题？** 检查 Terminal 的错误信息是解决问题的第一步！📋
