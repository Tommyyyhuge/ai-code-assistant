# 评测沙箱 seccomp 分语言策略 — 设计规格

> 日期: 2026-05-16  
> 关联问题: M11 (seccomp 白名单不完整)

---

## 一、问题

当前所有语言共用同一个 seccomp 白名单（37 syscall），对 C++ 偏保守，对 Python 则严重不足——Python 运行时需要大量 syscall（线程、动态加载、文件探测），白名单模式不可行。

## 二、行业参考

| 来源 | C++ | Python |
|------|-----|--------|
| QingdaoU/Judger | 白名单 25 个 | 黑名单（禁 fork/clone/kill/socket） |
| HustOJ | 白名单 ~50 个 | 黑名单 |
| Judge0/DMOJ | 白名单 | 白名单 + 大量额外 syscall |

**共识**: Python 不适合用白名单，C++ 适合。

## 三、方案

| 语言 | 策略 | 文件 |
|------|------|------|
| C++ | 白名单（37 → ~55） | `seccomp_cpp.json` |
| Python | 黑名单 | `seccomp_python.json` |

### 3.1 C++ 白名单（新增 ~18 个）

在现有 37 个基础上新增：

```
writev, readv, pread64      # vectorized IO
access, faccessat            # 文件权限检查
newfstatat, readlink         # 文件元数据
open, openat                 # 文件打开（运行时必须）
dup, dup2                    # fd 复制
madvise                      # 内存建议
tgkill                       # 线程信号
sched_getaffinity            # CPU 亲和性
getrusage                    # 资源使用（评测需要）
setrlimit, getrlimit         # 资源限制
```

### 3.2 Python 黑名单

```json
{
  "defaultAction": "SCMP_ACT_ALLOW",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": [
        "clone",      "fork",      "vfork",
        "kill",       "tkill",
        "socket",     "connect",   "bind",
        "execveat"
      ],
      "action": "SCMP_ACT_ERRNO"
    }
  ]
}
```

## 四、文件变更

| 文件 | 变更 |
|------|------|
| `judge/seccomp_cpp.json` | 从原 `seccomp.json` 扩展 |
| `judge/seccomp_python.json` | 新建黑名单配置 |
| `judge/seccomp.json` | 删除（被上面两个替代） |
| `judge/judge.sh` | accept `$6` seccomp profile 参数 |
| `app/services/judge_service.py` | 根据 language 传不同 profile |
| `app/tasks/judge_task.py` | 透传 profile 到 Docker run |
| `docker-compose.yml` | 挂载两个新 profile 文件 |

## 五、验证

1. C++ 评测正常通过（已是白名单不应有问题）
2. Python 评测正常通过（黑名单放行足够多）
3. Python 沙箱内尝试 `import os; os.fork()` → 被拦截
4. Python 沙箱内尝试 `import socket` → 无法连接

## 六、不计入

- 不做 syscall 参数级过滤（如 open 只允许 O_RDONLY）
- 不限制网络以外的其他资源（已在 docker run 参数中限制 CPU/内存）
