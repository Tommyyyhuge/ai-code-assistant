import type { Language } from '../types/language'

export const codeTemplates: Record<Language, string> = {
  python: '# 在此编写你的 Python 代码\n',
  cpp: '#include <iostream>\nusing namespace std;\n\nint main() {\n    // 在此编写你的 C++ 代码\n    return 0;\n}\n',
  c: '#include <stdio.h>\n\nint main() {\n    // 在此编写你的 C 代码\n    return 0;\n}\n',
  java: 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        // 在此编写你的 Java 代码\n    }\n}\n',
  javascript: '// 在此编写你的 JavaScript 代码\n',
  typescript: '// 在此编写你的 TypeScript 代码\n',
  go: 'package main\n\nimport "fmt"\n\nfunc main() {\n    // 在此编写你的 Go 代码\n}\n',
  rust: 'fn main() {\n    // 在此编写你的 Rust 代码\n}\n',
  php: '<?php\n// 在此编写你的 PHP 代码\n',
}
