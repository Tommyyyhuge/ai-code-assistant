# 前端集成提交代码功能设计文档

**日期**: 2026-05-15  
**版本**: MVP (Minimum Viable Product)  
**作者**: AI Assistant  

---

## 1. 概述

### 1.1 目标
在题目详情页（ProblemDetailPage）集成代码编辑器，允许用户编写代码并提交评测，实时查看评测结果。

### 1.2 范围
- ✅ 代码编辑器集成（复用现有 CodeEditor 组件）
- ✅ 语言选择器（复用现有 LanguageSelector 组件，限制为 C++/Python）
- ✅ 提交按钮 + 提交逻辑
- ✅ 评测结果轮询 + 展示
- ❌ 提交历史记录（后续迭代）
- ❌ 全局状态管理（使用本地 state）

---

## 2. 当前状态分析

### 2.1 前端现状
- **ProblemDetailPage**: 只展示题目描述，无代码编辑功能
- **CodeEditor**: 已存在，支持9种语言，动态导入
- **LanguageSelector**: 已存在，支持语言切换
- **API层**: 只有 `problemApi.getProblems()` 和 `problemApi.getProblem()`，无提交接口
- **状态管理**: ProblemStore（Zustand）管理题目列表和详情，无提交相关状态

### 2.2 后端现状
- **提交API**: 已就绪
  - `POST /api/submissions/` - 提交代码
  - `GET /api/submissions/{id}` - 查询提交状态
  - `GET /api/submissions/` - 获取提交列表
- **评测引擎**: Docker沙箱 + Celery异步队列，支持C++和Python
- **数据缺失**: 无测试用例数据（需要创建至少1个测试用例用于验证）

---

## 3. 设计方案

### 3.1 页面布局

ProblemDetailPage 改为左右分栏布局：

```
┌─────────────────────────────┬─────────────────────────────┐
│                             │  [LanguageSelector] [Submit]│
│    题目描述                  │                             │
│    ├── 描述                  │  ┌───────────────────────┐  │
│    ├── 输入格式              │  │                       │  │
│    ├── 输出格式              │  │    CodeEditor         │  │
│    ├── 约束条件              │  │                       │  │
│    └── 示例                  │  └───────────────────────┘  │
│                             │                             │
│                             │  ┌───────────────────────┐  │
│                             │  │  SubmissionResult     │  │
│                             │  │  Status: Judging...   │  │
│                             │  └───────────────────────┘  │
└─────────────────────────────┴─────────────────────────────┘
```

- **左侧（50%）**: 题目信息（原有内容）
- **右侧（50%）**: 代码编辑区 + 提交按钮 + 结果展示

### 3.2 组件清单

| 组件名 | 类型 | 来源 | 说明 |
|--------|------|------|------|
| CodeEditor | 复用 | 已存在 | 代码编辑器，支持语法高亮 |
| LanguageSelector | 复用 | 已存在 | 语言选择下拉框 |
| SubmitButton | 新增 | 本方案 | 提交按钮，显示提交状态 |
| SubmissionResult | 新增 | 本方案 | 评测结果展示卡片 |
| ProblemDetailPage | 修改 | 已存在 | 添加左右分栏布局 |

### 3.3 状态管理

使用 React 本地 state（不使用全局 Store）：

```typescript
// ProblemDetailPage 本地状态
const [code, setCode] = useState<string>("");
const [language, setLanguage] = useState<string>("cpp");
const [submission, setSubmission] = useState<Submission | null>(null);
const [isSubmitting, setIsSubmitting] = useState(false);
const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
```

### 3.4 提交流程

```
用户点击 Submit
    ↓
校验：代码非空、已选择语言
    ↓
POST /api/submissions/
    Body: { problem_id, code, language }
    ↓
返回：{ id, status: "pending", ... }
    ↓
设置 submission 状态
    ↓
开始轮询：每 2 秒 GET /api/submissions/{id}
    ↓
状态变为 "accepted" / "failed" / "error"
    ↓
更新 submission 状态，停止轮询
    ↓
显示结果
```

### 3.5 轮询机制

```typescript
// 轮询逻辑
const pollSubmission = useCallback(async (submissionId: string) => {
  const interval = setInterval(async () => {
    const result = await submissionApi.getSubmission(submissionId);
    setSubmission(result);
    
    // 如果评测完成，停止轮询
    if (["accepted", "failed", "error"].includes(result.status)) {
      clearInterval(interval);
      setPollingInterval(null);
      setIsSubmitting(false);
    }
  }, 2000); // 每 2 秒查询一次
  
  setPollingInterval(interval);
}, []);
```

### 3.6 错误处理

| 场景 | 处理方式 |
|------|----------|
| 代码为空 | 提交按钮禁用，或点击时提示 |
| 网络错误 | Toast 提示"提交失败，请重试" |
| 评测超时（>30秒） | 停止轮询，显示"评测超时" |
| 服务器错误 | 显示错误信息 |

---

## 4. API 接口定义

### 4.1 请求模型

```typescript
// types/submission.ts

export interface SubmissionCreate {
  problem_id: string;
  code: string;
  language: string; // "cpp" | "py"
}

export interface Submission {
  id: string;
  problem_id: string;
  code: string;
  language: string;
  status: "pending" | "judging" | "accepted" | "failed" | "error";
  score?: number;
  runtime_ms?: number;
  memory_kb?: number;
  passed_count?: number;
  total_count?: number;
  error_message?: string;
  submitted_at: string;
  judged_at?: string;
}
```

### 4.2 API 方法

```typescript
// services/submissionApi.ts

import axios from "axios";
import { Submission, SubmissionCreate } from "../types/submission";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

export const submissionApi = {
  submit: async (data: SubmissionCreate): Promise<Submission> => {
    const response = await axios.post(`${API_BASE}/api/submissions/`, data);
    return response.data;
  },
  
  getSubmission: async (id: string): Promise<Submission> => {
    const response = await axios.get(`${API_BASE}/api/submissions/${id}`);
    return response.data;
  }
};
```

---

## 5. 数据准备

### 5.1 测试用例

需要为现有题目创建至少1个测试用例：

```sql
-- 示例：为"两数之和"题目创建测试用例
INSERT INTO test_cases (id, problem_id, input_data, expected_output, order_index)
VALUES (
  gen_random_uuid(),
  (SELECT id FROM problems WHERE title = '两数之和'),
  '4 9\n2 7 11 15',
  '0 1',
  1
);
```

### 5.2 题目示例代码

为每道题目提供默认的代码模板：

**C++ 模板**:
```cpp
#include <iostream>
#include <vector>
using namespace std;

int main() {
    // 请在此处编写代码
    
    return 0;
}
```

**Python 模板**:
```python
# 请在此处编写代码

def main():
    pass

if __name__ == "__main__":
    main()
```

---

## 6. 文件变更清单

### 6.1 新增文件

| 文件路径 | 说明 |
|----------|------|
| `frontend/src/types/submission.ts` | 提交相关类型定义 |
| `frontend/src/services/submissionApi.ts` | 提交 API 接口 |
| `frontend/src/components/SubmissionResult.tsx` | 评测结果展示组件 |

### 6.2 修改文件

| 文件路径 | 修改内容 |
|----------|----------|
| `frontend/src/pages/ProblemDetailPage.tsx` | 添加左右分栏、提交逻辑、轮询 |
| `frontend/src/components/CodeEditor.tsx` | 可能调整高度/样式适配 |

### 6.3 后端数据

| 操作 | 说明 |
|------|------|
| 插入测试用例 | 为现有题目创建测试用例数据 |

---

## 7. 测试策略

### 7.1 手动测试步骤

1. 打开题目详情页
2. 选择语言（C++）
3. 编写代码（例如：输出 "Hello World"）
4. 点击 Submit
5. 观察状态变化：pending → judging → accepted/failed
6. 查看结果展示

### 7.2 边界情况

- 空代码提交
- 网络断开
- 评测超时
- 编译错误
- 答案错误

---

## 8. 后续迭代建议

### 8.1 P1（高优先级）
- 提交历史记录页面
- 全局 SubmissionStore（Zustand）
- 代码模板自动加载

### 8.2 P2（中优先级）
- WebSocket 实时推送结果
- 代码自动保存（localStorage）
- 运行测试（Run）vs 提交（Submit）

### 8.3 P3（低优先级）
- 代码执行时间/内存可视化
- 与正确答案的 diff 对比
- 排行榜功能

---

## 9. 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 后端 API 路径不一致 | 中 | 确认前缀为 `/api/submissions/` |
| 无测试用例数据 | 高 | 实施前必须创建至少1个测试用例 |
| Docker 沙箱性能 | 低 | MVP 阶段单用户测试无压力 |
| 轮询频率过高 | 低 | 2秒间隔，评测完成后立即停止 |

---

## 10. 成功标准

- [ ] 用户可以在题目详情页编写代码
- [ ] 用户可以选择语言（C++/Python）
- [ ] 用户可以提交代码
- [ ] 提交后显示评测状态（pending/judging/accepted/failed）
- [ ] 评测完成后显示分数和运行时间
- [ ] 端到端流程可重复执行

---

**设计文档完成。等待用户审查和批准。**
