# 🎯 DocuBot - Accounting FAQ Helper

**一个生产级的 AI FAQ 系统，专为会计办公室设计**

简洁的 Web UI + 智能检索 + LLM 过滤 = 97-100% 准确率 ✨

---

## 🚀 30 秒快速开始

### **Windows 用户**
```bash
# 直接双击
run_streamlit.bat
```

### **Mac/Linux 用户**
```bash
chmod +x run_streamlit.sh
./run_streamlit.sh
```

### **任何系统**
```bash
# PowerShell
.\run_streamlit.ps1

# 或手动
.\.venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Mac/Linux
python -m streamlit run app.py
```

✅ 浏览器自动打开到 http://localhost:8501

---

## 📚 文档导航

根据你的需求选择文档：

| 文档 | 用途 | 适合人群 |
|------|------|---------|
| **QUICKSTART_UI.md** | 30秒启动 + 常见任务 | 👤 最终用户 |
| **STREAMLIT_UI_GUIDE.md** | 完整 UI 功能说明 | 👨‍💼 办公室管理 |
| **TROUBLESHOOTING.md** | 问题排查和修复 | 🔧 IT 人员 |
| **STEP3_SUMMARY.md** | 技术架构细节 | 👨‍💻 开发者 |
| **README.md** | 项目背景信息 | 📖 学习者 |

---

## 🎯 核心功能

### 💬 Chat Interface
- 熟悉的聊天式界面
- 保留完整问答历史
- 实时反馈和错误提示

### 📚 Knowledge Base Browser
- 浏览所有文档
- 快速预览内容
- Markdown 格式支持

### 📋 Log Viewer
- 实时监控系统行为
- 4 种日志类型
- 可过滤查看

### 🧠 智能检索
- **Retrieval Mode**: 快速查询 (0.3s)
- **RAG Mode**: 智能过滤 (2-5s)
- 自动模式选择

### 🛡️ 安全防护
- SSN/EIN 检测
- 名字识别
- 查询日志记录

---

## 📊 项目结构

```
📦 DocuBot
├── 🌐 UI 层
│   ├── app.py                      主应用 (500行)
│   ├── run_streamlit.bat/ps1/sh    启动脚本
│   └── STREAMLIT_UI_GUIDE.md       UI 文档
│
├── 🧠 智能层
│   ├── docubot.py                  检索引擎
│   ├── llm_client.py               LLM 集成
│   ├── guardrail.py                安全防护
│   └── logger.py                   日志系统
│
├── 📚 知识库
│   └── docs_pt/                    Markdown 文档
│       ├── fees_2026.md
│       ├── irs_standard_deduction_2025.md
│       └── ...
│
├── 📖 文档
│   ├── README_FINAL.md             这个文件
│   ├── QUICKSTART_UI.md            快速指南
│   ├── STREAMLIT_UI_GUIDE.md       UI 详解
│   ├── TROUBLESHOOTING.md          问题排查
│   ├── STEP3_SUMMARY.md            技术细节
│   └── README.md                   项目背景
│
├── 📄 配置
│   ├── requirements.txt            依赖列表
│   ├── .env                        环境变量
│   └── .gitignore                  Git 配置
│
└── 🧪 测试工具
    ├── verify_step3_critical.py    快速验证
    └── step3_evaluation.py         完整测试
```

---

## 🏗️ 架构概览

```
┌─────────────────────────────────────┐
│     Streamlit Web UI (app.py)      │
│  ├─ Chat Interface                 │
│  ├─ Document Browser               │
│  └─ Log Viewer                     │
└────────────────┬────────────────────┘
                 │
┌────────────────┴────────────────────┐
│   Retrieval Engine (docubot.py)    │
│  ├─ Word Stemming                  │
│  ├─ TF-IDF Scoring                 │
│  ├─ N-gram Matching                │
│  └─ Threshold Filtering            │
└────────────────┬────────────────────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
  ┌──▼──┐  ┌──────▼───┐  ┌──▼──────┐
  │Guard│  │   LLM    │  │ Logger  │
  │rail │  │Filtering │  │  System │
  └──────┘  └──────────┘  └─────────┘
     │           │           │
     └───────────┼───────────┘
                 │
     ┌───────────▼──────────┐
     │  Knowledge Base      │
     │  (Markdown Files)    │
     └──────────────────────┘
```

---

## 📈 性能和准确率

### 检索准确率
- **Step 2** (检索): 36/39 = 92.3%
- **Step 3** (RAG): 38-39/39 = 97-100%

### 查询性能
| 操作 | 时间 |
|------|------|
| Retrieval Mode | 0.3-0.8s |
| RAG Mode | 2-5s |
| 文档预览 | 0.1s |
| 启动时间 | 5-10s |

---

## 🔒 安全功能

```
三层防护机制

第1层: 输入验证 (Input Guardrail)
├─ SSN 检测: XXX-XX-XXXX
├─ EIN 检测: XX-XXXXXXX
└─ 名字检测: 大写 + 上下文

第2层: 检索过滤 (Retrieval Safety)
├─ 得分阈值: ≥ 3.0
└─ 否定检测: "不", "没有", "无"

第3层: LLM 推理 (LLM Judgment)
├─ 明确示例指导
├─ 拒绝短语: "Not covered"
└─ 强制语义理解
```

---

## 🛠️ 开发者快速指南

### 安装依赖
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # 或 source venv/bin/activate
pip install -r requirements.txt
```

### 验证系统
```bash
# 快速验证 4 个关键测试
python verify_step3_critical.py

# 完整测试 39 个案例
python step3_evaluation.py
```

### 测试组件
```bash
# 检索
python -c "from docubot import DocuBot; DocuBot(docs_folder='docs_pt')"

# LLM
python -c "from llm_client import GeminiClient; GeminiClient()"

# 防护
python -c "from guardrail import check_input_safety; check_input_safety('test')"

# 日志
python -c "from logger import get_logger; get_logger()"
```

---

## 🚨 常见问题

### Q: "'streamlit' 不是内部或外部命令"
**A:** 看 TROUBLESHOOTING.md 中的快速修复。要点：使用 `python -m streamlit` 而不是直接 `streamlit`

### Q: 为什么查询这么慢？
**A:** RAG 模式需要调用 Gemini API。如果响应慢：
- 检查网络连接
- 或切换到 Retrieval Only 模式

### Q: 如何添加新文档？
**A:** 
1. 把 `.md` 文件放到 `docs_pt/` 文件夹
2. 重启应用
3. 新文件会自动出现在侧栏

### Q: 日志在哪里？
**A:** 项目根目录的 `.jsonl` 文件：
- `guardrail_blocks.jsonl` - 被拦截的查询
- `retrieval_results.jsonl` - 检索结果

### Q: 怎样修改应用界面？
**A:** 编辑 `app.py`：
- 修改标题：第 16 行的 `page_title`
- 改颜色：第 26-47 行的 CSS
- 改说明：搜索 `st.markdown()`

---

## 📞 支持和反馈

### 遇到问题？

1. **首先** - 查看 TROUBLESHOOTING.md
2. **其次** - 检查 Terminal 的错误信息
3. **再次** - 读一遍相关文档
4. **最后** - 尝试完整重置（见 TROUBLESHOOTING.md）

### 想要改进？

1. 检查 `guardrail_blocks.jsonl` 中的被拦截查询
2. 分析 `retrieval_results.jsonl` 中的失败案例
3. 修改提示或知识库
4. 重新测试

---

## 📋 检查清单

在投入生产使用前：

- [ ] 成功启动 Streamlit 应用
- [ ] 测试简单查询（"标准扣除额"）
- [ ] 测试被拒绝的查询（"家具折旧"）
- [ ] 浏览知识库文件
- [ ] 检查日志记录
- [ ] 在两种模式间切换
- [ ] 运行 `verify_step3_critical.py` 验证
- [ ] 设置 GEMINI_API_KEY 使用 RAG 模式
- [ ] 员工培训完毕

---

## 🎓 学习路径

**新手（刚开始用）：**
1. 读 QUICKSTART_UI.md
2. 双击 run_streamlit.bat
3. 开始提问！

**管理员（想深入了解）：**
1. 读 STREAMLIT_UI_GUIDE.md
2. 检查日志 (.jsonl 文件)
3. 阅读 STEP3_SUMMARY.md

**开发者（想修改代码）：**
1. 读 README.md (项目背景)
2. 读 STEP3_SUMMARY.md (架构)
3. 查看代码注释在 app.py, docubot.py, llm_client.py

---

## 🎉 项目成果

从零到生产级系统：

✅ **准确率**：从 0% 到 97-100%
✅ **安全性**：三层防护，无 PII 泄露  
✅ **可用性**：现代 Web UI，即开即用
✅ **可维护性**：完整日志，易于分析改进
✅ **可扩展性**：模块化架构，易于定制

---

## 📜 许可证和致谢

This project was built as part of CodePath AI110 Module 4 Tinker Activity.

**Key Components:**
- DocuBot: Custom retrieval engine (Step 2)
- LLM Integration: Google Gemini API
- UI: Streamlit framework
- Logging: JSONL format

---

## 🚀 下一步

当前系统（Step 3）已达到 97-100% 准确率。

潜在改进方向：

1. **多轮对话** - 允许员工追问
2. **置信度评分** - 区分高/低置信回答
3. **反馈循环** - 用户标记有用/无用的答案
4. **日志分析** - 自动识别失败模式
5. **知识库扩展** - 添加新的 FAQ 类别
6. **本地化** - 支持多种语言

---

**Happy querying! 💬✨**

最后更新: 2026-11-15
版本: 1.0 (Production Ready)
