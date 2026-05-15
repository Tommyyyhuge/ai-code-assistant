import { useState, useEffect, useMemo } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { oneDark } from '@codemirror/theme-one-dark'
import { javascript } from '@codemirror/lang-javascript'
import type { Extension } from '@codemirror/state'
import type { Language } from '../types/language'

interface CodeEditorProps {
  code: string
  language: Language
  onChange: (value: string) => void
  readOnly?: boolean
  height?: string
}

const languageLoaders: Record<string, () => Promise<Extension>> = {
  c: () => import('@codemirror/lang-cpp').then(m => m.cpp()),
  cpp: () => import('@codemirror/lang-cpp').then(m => m.cpp()),
  python: () => import('@codemirror/lang-python').then(m => m.python()),
  java: () => import('@codemirror/lang-java').then(m => m.java()),
  javascript: () => import('@codemirror/lang-javascript').then(m => m.javascript()),
  typescript: () => import('@codemirror/lang-javascript').then(m => m.javascript({ typescript: true })),
  go: () => import('@codemirror/lang-go').then(m => m.go()),
  rust: () => import('@codemirror/lang-rust').then(m => m.rust()),
  php: () => import('@codemirror/lang-php').then(m => m.php()),
}

export default function CodeEditor({
  code,
  language,
  onChange,
  readOnly = false,
  height = '400px',
}: CodeEditorProps) {
  const [languageExtension, setLanguageExtension] = useState<Extension | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    const loadLanguage = async () => {
      if (!cancelled) {
        setIsLoading(true)
      }

      const loader = languageLoaders[language]
      if (!loader) {
        if (!cancelled) {
          setLanguageExtension(javascript())
          setIsLoading(false)
        }
        return
      }

      try {
        const ext = await loader()
        if (!cancelled) {
          setLanguageExtension(ext)
          setIsLoading(false)
        }
      } catch (error) {
        console.error(`Failed to load language ${language}:`, error)
        if (!cancelled) {
          setLanguageExtension(javascript())
          setIsLoading(false)
        }
      }
    }

    loadLanguage()
    return () => { cancelled = true }
  }, [language])

  const extensions = useMemo(() => {
    return languageExtension ? [languageExtension] : []
  }, [languageExtension])

  if (isLoading) {
    return (
      <div className="rounded-lg overflow-hidden border border-gray-700 bg-gray-800" style={{ height }}>
        <div className="flex items-center justify-center h-full text-gray-400">
          加载编辑器...
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-lg overflow-hidden border border-gray-700">
      <CodeMirror
        value={code}
        height={height}
        theme={oneDark}
        extensions={extensions}
        onChange={onChange}
        readOnly={readOnly}
        basicSetup={{
          lineNumbers: true,
          highlightActiveLineGutter: true,
          highlightActiveLine: true,
          foldGutter: true,
          autocompletion: true,
          bracketMatching: true,
          closeBrackets: true,
          indentOnInput: true,
          tabSize: 2,
        }}
      />
    </div>
  )
}
