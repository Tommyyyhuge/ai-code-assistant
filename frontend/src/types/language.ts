export type Language =
  | 'c'
  | 'cpp'
  | 'python'
  | 'java'
  | 'javascript'
  | 'typescript'
  | 'go'
  | 'rust'
  | 'php'

export interface LanguageOption {
  value: Language
  label: string
  extension: string
}

export const languages: LanguageOption[] = [
  { value: 'python', label: 'Python', extension: 'py' },
  { value: 'cpp', label: 'C++', extension: 'cpp' },
  { value: 'c', label: 'C', extension: 'c' },
  { value: 'java', label: 'Java', extension: 'java' },
  { value: 'javascript', label: 'JavaScript', extension: 'js' },
  { value: 'typescript', label: 'TypeScript', extension: 'ts' },
  { value: 'go', label: 'Go', extension: 'go' },
  { value: 'rust', label: 'Rust', extension: 'rs' },
  { value: 'php', label: 'PHP', extension: 'php' },
] as const
