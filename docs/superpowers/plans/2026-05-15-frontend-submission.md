# 前端集成提交代码功能 Implementation Plan

> **For agentic work**: This plan is designed for delegation to sub-agents. Each task is self-contained and includes specific file paths, code patterns, and success criteria.

**Spec**: [2026-05-15-frontend-submission-design.md](../specs/2026-05-15-frontend-submission-design.md)  
**Date**: 2026-05-15  
**Estimated Duration**: 45-60 minutes  
**Parallel Tasks**: Tasks 1-3 can run in parallel. Tasks 4-7 are sequential.

---

## Overview

在题目详情页（ProblemDetailPage）集成代码编辑器，允许用户编写代码、选择语言、提交评测，并实时查看评测结果。

### Scope
- ✅ 代码编辑器集成（复用现有组件）
- ✅ 语言选择器（限制为 C++/Python）
- ✅ 提交按钮 + 提交逻辑
- ✅ 评测结果轮询 + 展示
- ❌ 提交历史记录（后续迭代）
- ❌ 全局状态管理（使用本地 state）

---

## File Structure

### New Files (3)
| File | Responsibility |
|------|---------------|
| `frontend/src/types/submission.ts` | 提交相关 TypeScript 类型定义 |
| `frontend/src/services/submissionApi.ts` | 提交 API 接口（axios 封装） |
| `frontend/src/components/SubmissionResult.tsx` | 评测结果展示组件 |

### Modified Files (1)
| File | Responsibility |
|------|---------------|
| `frontend/src/pages/ProblemDetailPage.tsx` | 添加左右分栏布局、提交逻辑、轮询机制 |

### Data Preparation (1)
| Operation | Responsibility |
|-----------|---------------|
| Insert test cases | 为现有题目创建测试用例数据 |

---

## Prerequisites

- [ ] 后端服务运行（PostgreSQL + Redis + FastAPI）
- [ ] 前端开发服务器可启动
- [ ] Docker 沙箱镜像已构建（`judge-sandbox:latest`）

---

## Tasks

### Task 1: 创建提交类型定义
**File**: `frontend/src/types/submission.ts`

```typescript
export interface SubmissionCreate {
  problem_id: string;
  code: string;
  language: string;
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

**Success Criteria**:
- [ ] 文件创建成功
- [ ] TypeScript 编译无错误

---

### Task 2: 创建提交 API 服务
**File**: `frontend/src/services/submissionApi.ts`

```typescript
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

**Success Criteria**:
- [ ] 文件创建成功
- [ ] 可以正确导入 `Submission` 和 `SubmissionCreate` 类型
- [ ] API 方法签名正确

---

### Task 3: 创建评测结果展示组件
**File**: `frontend/src/components/SubmissionResult.tsx`

```typescript
import React from "react";
import { Submission } from "../types/submission";

interface SubmissionResultProps {
  submission: Submission | null;
  isSubmitting: boolean;
}

const SubmissionResult: React.FC<SubmissionResultProps> = ({
  submission,
  isSubmitting,
}) => {
  if (!submission && !isSubmitting) {
    return null;
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "accepted":
        return "text-green-600 bg-green-50";
      case "failed":
        return "text-red-600 bg-red-50";
      case "error":
        return "text-orange-600 bg-orange-50";
      case "judging":
        return "text-blue-600 bg-blue-50";
      case "pending":
        return "text-gray-600 bg-gray-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "accepted":
        return "通过";
      case "failed":
        return "未通过";
      case "error":
        return "错误";
      case "judging":
        return "评测中...";
      case "pending":
        return "等待中...";
      default:
        return status;
    }
  };

  if (isSubmitting && !submission) {
    return (
      <div className="mt-4 p-4 rounded-lg bg-gray-50 border border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          <span className="text-gray-600">提交中...</span>
        </div>
      </div>
    );
  }

  if (!submission) return null;

  return (
    <div className="mt-4 p-4 rounded-lg border border-gray-200">
      <div className="flex items-center justify-between mb-2">
        <span
          className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
            submission.status
          )}`}
        >
          {getStatusText(submission.status)}
        </span>
        {submission.score !== undefined && (
          <span className="text-sm text-gray-600">
            得分: {submission.score}%
          </span>
        )}
      </div>

      {(submission.status === "accepted" || submission.status === "failed") && (
        <div className="grid grid-cols-3 gap-4 mt-3 text-sm">
          {submission.runtime_ms !== undefined && (
            <div>
              <span className="text-gray-500">运行时间:</span>
              <span className="ml-1 font-medium">{submission.runtime_ms}ms</span>
            </div>
          )}
          {submission.memory_kb !== undefined && (
            <div>
              <span className="text-gray-500">内存:</span>
              <span className="ml-1 font-medium">
                {Math.round(submission.memory_kb / 1024)}MB
              </span>
            </div>
          )}
          {submission.passed_count !== undefined && (
            <div>
              <span className="text-gray-500">通过:</span>
              <span className="ml-1 font-medium">
                {submission.passed_count}/{submission.total_count}
              </span>
            </div>
          )}
        </div>
      )}

      {submission.error_message && (
        <div className="mt-3 p-2 bg-red-50 rounded text-sm text-red-700">
          {submission.error_message}
        </div>
      )}
    </div>
  );
};

export default SubmissionResult;
```

**Success Criteria**:
- [ ] 组件渲染正常
- [ ] 不同状态显示不同颜色和文本
- [ ] 显示运行时间、内存、通过数量
- [ ] 错误信息正确显示

---

### Task 4: 修改 ProblemDetailPage
**File**: `frontend/src/pages/ProblemDetailPage.tsx`

在现有页面基础上，添加：

1. **导入新增模块**:
```typescript
import { useState, useEffect, useCallback } from "react";
import CodeEditor from "../components/CodeEditor";
import LanguageSelector from "../components/LanguageSelector";
import SubmissionResult from "../components/SubmissionResult";
import { submissionApi } from "../services/submissionApi";
import { Submission } from "../types/submission";
```

2. **添加本地状态**:
```typescript
const [code, setCode] = useState<string>("");
const [language, setLanguage] = useState<string>("cpp");
const [submission, setSubmission] = useState<Submission | null>(null);
const [isSubmitting, setIsSubmitting] = useState(false);
```

3. **添加提交处理函数**:
```typescript
const handleSubmit = async () => {
  if (!code.trim()) {
    alert("请先编写代码");
    return;
  }

  setIsSubmitting(true);
  setSubmission(null);

  try {
    const result = await submissionApi.submit({
      problem_id: id!,
      code,
      language,
    });
    setSubmission(result);

    // 开始轮询
    if (result.id) {
      pollSubmission(result.id);
    }
  } catch (error) {
    console.error("提交失败:", error);
    alert("提交失败，请重试");
    setIsSubmitting(false);
  }
};
```

4. **添加轮询函数**:
```typescript
const pollSubmission = useCallback((submissionId: string) => {
  const interval = setInterval(async () => {
    try {
      const result = await submissionApi.getSubmission(submissionId);
      setSubmission(result);

      // 如果评测完成，停止轮询
      if (["accepted", "failed", "error"].includes(result.status)) {
        clearInterval(interval);
        setIsSubmitting(false);
      }
    } catch (error) {
      console.error("轮询失败:", error);
      clearInterval(interval);
      setIsSubmitting(false);
    }
  }, 2000);

  // 30秒后自动停止轮询
  setTimeout(() => {
    clearInterval(interval);
    setIsSubmitting(false);
  }, 30000);
}, []);
```

5. **修改布局为左右分栏**:
```typescript
return (
  <div className="container mx-auto px-4 py-8">
    <div className="flex gap-6">
      {/* 左侧：题目信息 */}
      <div className="w-1/2">
        {/* 原有题目信息内容 */}
      </div>

      {/* 右侧：代码编辑区 */}
      <div className="w-1/2">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <LanguageSelector
              selectedLanguage={language}
              onLanguageChange={setLanguage}
            />
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
            >
              {isSubmitting ? "提交中..." : "提交"}
            </button>
          </div>

          <CodeEditor
            code={code}
            language={language}
            onChange={setCode}
            height="400px"
          />

          <SubmissionResult
            submission={submission}
            isSubmitting={isSubmitting}
          />
        </div>
      </div>
    </div>
  </div>
);
```

**Success Criteria**:
- [ ] 页面显示左右分栏布局
- [ ] CodeEditor 正确渲染
- [ ] LanguageSelector 正常工作
- [ ] Submit 按钮可点击
- [ ] 提交后显示状态
- [ ] 轮询机制正常工作

---

### Task 5: 创建测试用例数据
**Operation**: 插入数据库

为现有题目创建测试用例：

```sql
-- 为"两数之和"创建测试用例
INSERT INTO test_cases (id, problem_id, input_data, expected_output, order_index, created_at)
VALUES (
  gen_random_uuid(),
  (SELECT id FROM problems WHERE title = '两数之和'),
  '4 9\n2 7 11 15',
  '0 1',
  1,
  NOW()
);

-- 为"反转字符串"创建测试用例
INSERT INTO test_cases (id, problem_id, input_data, expected_output, order_index, created_at)
VALUES (
  gen_random_uuid(),
  (SELECT id FROM problems WHERE title = '反转字符串'),
  'hello',
  'olleh',
  1,
  NOW()
);
```

**Success Criteria**:
- [ ] 测试用例插入成功
- [ ] 查询 `SELECT * FROM test_cases` 返回数据

---

### Task 6: 前端构建验证
**Command**: `cd D:\AI_code_assistant\frontend && npm run build`

**Success Criteria**:
- [ ] 构建成功，无 TypeScript 错误
- [ ] 无 ESLint 错误

---

### Task 7: 端到端测试
**Steps**:

1. 启动后端服务
2. 启动前端开发服务器
3. 打开浏览器访问 `http://localhost:3000/problems`
4. 点击任意题目进入详情页
5. 选择语言（C++）
6. 编写代码：
   ```cpp
   #include <iostream>
   int main() {
       std::cout << "Hello World" << std::endl;
       return 0;
   }
   ```
7. 点击"提交"
8. 观察状态变化：pending → judging → accepted/failed
9. 查看结果展示

**Success Criteria**:
- [ ] 可以正常提交代码
- [ ] 状态正确更新
- [ ] 结果显示正常
- [ ] 无 JavaScript 错误

---

## Testing Strategy

### Manual Test Cases

| # | 场景 | 步骤 | 预期结果 |
|---|------|------|----------|
| 1 | 正常提交 | 编写代码 → 点击提交 | 显示"提交中..." → 显示结果 |
| 2 | 空代码提交 | 不编写代码 → 点击提交 | 提示"请先编写代码" |
| 3 | 切换语言 | 选择 Python → 编写 Python 代码 → 提交 | 使用 Python 评测 |
| 4 | 快速连续提交 | 点击提交 → 立即再次点击 | 按钮禁用，防止重复提交 |
| 5 | 网络错误 | 断开网络 → 点击提交 | 提示"提交失败，请重试" |

---

## Rollback Plan

如果实施过程中出现问题：

1. **Git 回滚**: `git checkout -- frontend/src/pages/ProblemDetailPage.tsx`
2. **删除新增文件**:
   - `frontend/src/types/submission.ts`
   - `frontend/src/services/submissionApi.ts`
   - `frontend/src/components/SubmissionResult.tsx`
3. **恢复数据库**: 删除测试用例 `DELETE FROM test_cases WHERE problem_id IN (...)`

---

## Post-Implementation

### 下一步（后续迭代）
- [ ] 添加 SubmissionStore（Zustand）管理全局提交状态
- [ ] 创建 SubmissionListPage 查看历史提交
- [ ] 添加代码模板自动加载功能
- [ ] 支持 WebSocket 实时推送结果

### 监控指标
- 提交成功率
- 平均评测时间
- 页面加载性能

---

**计划完成。准备执行。**
