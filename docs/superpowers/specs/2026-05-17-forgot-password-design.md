# 忘记密码 / 验证码重置 — 设计规格

> 日期: 2026-05-17  
> 关联: 认证系统增强

---

## 一、流程

```
登录页 → 点击"忘记密码" → 输入邮箱 → 收到 6 位验证码邮件
    → 输入验证码 + 新密码 → 密码重置成功 → 跳回登录页
```

---

## 二、后端 API

### 2.1 `POST /api/v1/auth/forgot-password`

请求：
```json
{ "email": "user@example.com" }
```

逻辑：
1. 查邮箱是否存在 → 不存在仍返回 200（防枚举）
2. 生成 6 位数字验证码
3. 存入 Redis：`reset_code:{email}` = code，TTL 600s
4. 通过 SMTP 发送验证码邮件
5. 返回 `{ "message": "验证码已发送" }`

速率限制：`3/minute`

### 2.2 `POST /api/v1/auth/reset-password`

请求：
```json
{ "email": "user@example.com", "code": "123456", "new_password": "NewP@ss1" }
```

逻辑：
1. 从 Redis 读取 `reset_code:{email}`，校验验证码
2. 验证码错误/过期 → 400
3. 验证新密码强度（复用 `_validate_password_strength`）
4. 更新用户 `password_hash`
5. 删除 Redis 中的验证码（一次性）
6. 返回 `{ "message": "密码重置成功" }`

速率限制：`5/minute`

---

## 三、配置

### 3.1 config.py 新增

```python
SMTP_HOST: str = "smtp.qq.com"
SMTP_PORT: int = 587
SMTP_USER: str = ""
SMTP_PASSWORD: str = ""
```

### 3.2 .env.example 新增

```
# ── 邮件 ──
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
```

### 3.3 docker-compose.yml

后端服务 environment 新增 SMTP 环境变量。

---

## 四、前端

### 4.1 LoginForm.tsx

密码输入框下方添加：
```tsx
<Link to="/forgot-password" className="text-sm text-blue-600 hover:underline">
  忘记密码？
</Link>
```

### 4.2 ForgotPasswordPage.tsx（新文件）

两步表单：

**步骤 1 — 输入邮箱**
- 邮箱输入框 + "发送验证码" 按钮
- 调用 `POST /auth/forgot-password`
- 成功后进入步骤 2

**步骤 2 — 输入验证码 + 新密码**
- 6 位验证码输入框
- 新密码 + 确认密码
- "重置密码" 按钮
- 调用 `POST /auth/reset-password`
- 成功后跳转 `/login` 并提示

### 4.3 App.tsx

新增路由：
```tsx
<Route path="/forgot-password" element={<ForgotPasswordPage />} />
```

---

## 五、防滥用

| 端点 | 速率限制 | 验证码有效期 | 验证码次数 |
|------|---------|-------------|-----------|
| forgot-password | 3/min | 10 分钟 | 每次覆盖 |
| reset-password | 5/min | — | 一次有效即删除 |

- 邮箱不存在时不报错（防用户枚举）
- 验证码连续错误 5 次后删除（防暴力破解）

---

## 六、邮件模板

主题：`AI Code Assistant - 密码重置验证码`

正文：
```
您的验证码是：123456
有效期 10 分钟，请勿泄露给他人。
```

---

## 七、不计入范围

- ❌ 邮件发送失败重试
- ❌ 邮件模板自定义
- ❌ 手机短信验证
