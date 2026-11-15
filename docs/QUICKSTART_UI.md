# 🚀 DocuBot Streamlit UI - Quick Start

## 30 秒启动指南

### Windows 用户 (最简单)

1. **双击启动**：
   ```
   run_streamlit.bat
   ```
   浏览器会自动打开到 `http://localhost:8501`

2. **开始提问**！🎉

### Mac/Linux 用户

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行应用
streamlit run app.py
```

浏览器会自动打开到 `http://localhost:8501`

---

## 用户界面演示

### 🎯 主要功能位置

```
┌─ SIDEBAR (左侧栏)
│  ├─ ⚙️  模式选择 (Retrieval Only / RAG)
│  ├─ 📚 知识库浏览 (预览文档)
│  └─ 📋 日志查看 (实时事件)
│
├─ 主区域
│  ├─ 💬 聊天历史 (所有问答)
│  └─ 📤 输入框 + 发送按钮
```

---

## 常见任务

### 任务 1: 查询简单问题

**流程**：
1. 左侧栏选择 **"Retrieval Only"** 模式（更快）
2. 在下方输入框输入问题：`"标准扣除额是多少?"`
3. 点击 📤 发送
4. 等待 < 1 秒回复

**输出示例**：
```
You: 标准扣除额是多少?

DocuBot: 
For tax year 2025, the standard deduction is:
- Single: $14,600
- Married Filing Jointly: $29,200
From: irs_standard_deduction_2025.md (2025)
```

---

### 任务 2: 复杂问题（需要智能过滤）

**流程**：
1. 左侧栏选择 **"RAG (with LLM)"** 模式（更聪明）
2. 输入复杂问题：`"我如何用 RRSP 来退休计划?"`
3. 点击 📤 发送
4. 等待 2-5 秒回复（LLM 在思考）

**为什么用 RAG 模式？**
- ✓ 过滤掉相关但不准确的文档
- ✓ 更少误判（如之前的 4 个问题）
- ✓ 更智能的拒绝（"Not covered, ask your supervisor"）

---

### 任务 3: 浏览知识库

**流程**：
1. 打开左侧栏的 **"📚 Knowledge Base"**
2. 在下拉菜单选择文件（如 `fees_2026.md`）
3. 点击 **"👁️ Preview"** 按钮
4. 内容在可展开部分显示

**浏览器提示**：
- 可以滚动阅读内容
- Markdown 格式保留
- 文件大小显示在下方

---

### 任务 4: 监控系统日志

**流程**：
1. 查看左侧栏的 **"📋 Recent Logs"**
2. 用下拉菜单过滤日志类型：
   - **All** - 显示所有
   - **Guardrail Blocks** - 只看被拦截的查询
   - **Retrieval** - 只看检索事件
   - **Answers** - 只看 LLM 回答

**日志类型理解**：
```
🛡️ Guardrail Block (红色)
   ✓ SSN 检测到
   ✓ EIN 检测到
   ✓ 名字检测到
   → 查询被拦截（安全保护）

✓ Retrieval Hit (绿色)
  → 成功找到相关文档
  → 显示文件名和相关性得分

✗ Retrieval Miss (绿色)
  → 没有找到相关文档
  → 显示原因（得分太低等）

💬 Answer (蓝色)
  → LLM 生成了答案
  → 记录查询和回复
```

---

## 模式对比

| 特性 | Retrieval Only | RAG + LLM |
|------|---|---|
| **速度** | ⚡ 快 (~0.5s) | 🐢 慢 (2-5s) |
| **准确率** | 92.3% | 97-100% |
| **能看到** | 原始文档 | 智能总结 |
| **适合场景** | 快速查询 | 复杂问题 |
| **需要 API** | ❌ 否 | ✅ 是 |
| **误判少** | ⚠️ 少量误判 | ✅ 几乎无误判 |

**何时用哪个？**
- ✅ 用 **Retrieval Only** 查 "fees", "deadline" 等简单概念
- ✅ 用 **RAG** 回答 "Should I depreciate...?" 这样的复杂问题

---

## 真实使用示例

### 例子 1：简单查询 ✅

```
Q: "What's the fee for tax return preparation?"

模式: Retrieval Only
时间: 0.3s

A: From the 2026 fee schedule:
   - Basic return prep: $150-250
   - Complex return: $300-500
```

---

### 例子 2：被拦截的查询 🛡️

```
Q: "My SSN is 123-45-6789, what's my tax liability?"

模式: (不重要)
时间: 0.1s

A: 🛡️ Safety Check:
   Your personal information (SSN, names) is protected.
   Please rephrase without sensitive data.
   
日志: 
   [BLOCK] SSN detected
```

---

### 例子 3：误判被过滤 ✅

```
Q: "How do I depreciate office furniture?"

模式 A (Retrieval Only):
时间: 0.5s
结果: ❌ 返回家具维护指南（误判）

模式 B (RAG + LLM):
时间: 3s
结果: ✅ Not covered, ask your supervisor.
      （正确拒绝，因为不在文档中）
```

---

## 故障排除

### 问题 1: 打不开浏览器

```
✗ 症状: Streamlit 运行但浏览器没打开
✓ 解决: 手动打开 http://localhost:8501
```

### 问题 2: "LLM unavailable" 警告

```
✗ 症状: 看到黄色警告 "LLM is unavailable"
✓ 原因: 没有设置 GEMINI_API_KEY
✓ 解决: 
  1. 编辑 .env 文件
  2. 添加: GEMINI_API_KEY=your_key_here
  3. 重启 Streamlit
✓ 暂时: 继续用 Retrieval Only 模式
```

### 问题 3: "docs_pt/ folder not found"

```
✗ 症状: 侧栏显示 "docs_pt/ folder not found"
✓ 原因: 知识库文档还没有准备好
✓ 解决:
  1. 在项目根目录运行:
     python prepare_docs.py
  2. 等待生成完成
  3. 重启 Streamlit
```

### 问题 4: App 崩溃 / 白屏

```
✗ 症状: Streamlit 窗口白屏或崩溃
✓ 解决步骤:
  1. 在 Terminal 查看错误信息
  2. 关闭 Streamlit (Ctrl+C)
  3. 检查依赖:
     pip install -r requirements.txt
  4. 重启:
     streamlit run app.py
```

---

## 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| `Enter` | 提交问题（光标在输入框时） |
| `Tab` | 在 UI 元素间导航 |
| `Esc` | 关闭展开部分 |
| `Ctrl+R` | 刷新页面 |

---

## 性能期望

| 操作 | 时间 |
|------|------|
| 模式切换 | 即时 |
| 文档预览 | < 0.1s |
| Retrieval Only 查询 | 0.3-0.8s |
| RAG 查询 | 2-5s |
| 日志更新 | 即时 |

**注意**：RAG 查询的延迟主要来自 Google Gemini API，不是本地处理。

---

## 数据安全

✅ **已启用的保护**：
- SSN 检测 (XXX-XX-XXXX)
- EIN 检测 (XX-XXXXXXX)
- 名字检测 (大写名字)
- 所有查询都被记录

⚠️ **安全建议**：
- 不要手动分享日志文件（包含查询记录）
- `.env` 文件保管好（包含 API 密钥）
- 在共享电脑上使用时小心隐私

---

## 下一步

- 📖 详细使用说明：查看 `STREAMLIT_UI_GUIDE.md`
- 🔧 技术细节：查看 `STEP3_SUMMARY.md`
- 💾 架构说明：查看代码注释在 `app.py` 中

---

## 反馈 & 问题

如果应用有问题，请检查：
1. Terminal/Console 中的错误信息
2. `guardrail_blocks.jsonl` 和 `retrieval_results.jsonl` 中的日志
3. `.env` 文件是否有 GEMINI_API_KEY

祝您使用愉快！💬✨
