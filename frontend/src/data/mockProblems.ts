export type Difficulty = 'easy' | 'medium' | 'hard'

export interface Problem {
  id: string
  title: string
  difficulty: Difficulty
  tags: string[]
  acceptanceRate: number
  totalSubmissions: number
  description: string
}

export const problems: Problem[] = [
  {
    id: '1',
    title: '两数之和',
    difficulty: 'easy',
    tags: ['数组', '哈希表'],
    acceptanceRate: 0.65,
    totalSubmissions: 15200,
    description: '给定一个整数数组和一个目标值，找出数组中和为目标值的两个数。',
  },
  {
    id: '2',
    title: '最长无重复子串',
    difficulty: 'medium',
    tags: ['字符串', '滑动窗口', '哈希表'],
    acceptanceRate: 0.42,
    totalSubmissions: 23100,
    description: '给定一个字符串，找出不含有重复字符的最长子串的长度。',
  },
  {
    id: '3',
    title: '合并两个有序链表',
    difficulty: 'easy',
    tags: ['链表', '递归'],
    acceptanceRate: 0.78,
    totalSubmissions: 18900,
    description: '将两个升序链表合并为一个新的升序链表。',
  },
  {
    id: '4',
    title: '最长回文子串',
    difficulty: 'medium',
    tags: ['字符串', '动态规划'],
    acceptanceRate: 0.35,
    totalSubmissions: 19800,
    description: '给定一个字符串，找到最长的回文子串。',
  },
  {
    id: '5',
    title: '接雨水',
    difficulty: 'hard',
    tags: ['数组', '双指针', '动态规划', '栈'],
    acceptanceRate: 0.28,
    totalSubmissions: 12400,
    description: '给定 n 个非负整数表示每个宽度为 1 的柱子的高度图，计算按此排列的柱子下雨之后能接多少雨水。',
  },
  {
    id: '6',
    title: '二叉树的中序遍历',
    difficulty: 'easy',
    tags: ['树', '栈', '递归'],
    acceptanceRate: 0.82,
    totalSubmissions: 16700,
    description: '给定一个二叉树的根节点，返回它的中序遍历。',
  },
  {
    id: '7',
    title: '每日温度',
    difficulty: 'medium',
    tags: ['数组', '栈', '单调栈'],
    acceptanceRate: 0.55,
    totalSubmissions: 14300,
    description: '给定一个整数数组 temperatures，表示每天的温度，返回一个数组 answer，其中 answer[i] 是指对于第 i 天，下一个更高温度出现在几天后。',
  },
  {
    id: '8',
    title: '编辑距离',
    difficulty: 'hard',
    tags: ['字符串', '动态规划'],
    acceptanceRate: 0.22,
    totalSubmissions: 9800,
    description: '给你两个单词 word1 和 word2，请返回将 word1 转换成 word2 所使用的最少操作数。',
  },
  {
    id: '9',
    title: '有效的括号',
    difficulty: 'easy',
    tags: ['字符串', '栈'],
    acceptanceRate: 0.88,
    totalSubmissions: 21500,
    description: '给定一个只包括 (，)，{，}，[，] 的字符串 s，判断字符串是否有效。',
  },
  {
    id: '10',
    title: '全排列',
    difficulty: 'medium',
    tags: ['数组', '回溯'],
    acceptanceRate: 0.48,
    totalSubmissions: 17600,
    description: '给定一个不含重复数字的数组 nums，返回其所有可能的全排列。',
  },
  {
    id: '11',
    title: '最小覆盖子串',
    difficulty: 'hard',
    tags: ['字符串', '滑动窗口', '哈希表'],
    acceptanceRate: 0.19,
    totalSubmissions: 8900,
    description: '给定两个字符串 s 和 t，返回 s 中涵盖 t 所有字符的最小子串。',
  },
  {
    id: '12',
    title: '反转链表',
    difficulty: 'easy',
    tags: ['链表', '递归'],
    acceptanceRate: 0.91,
    totalSubmissions: 20100,
    description: '给你单链表的头节点 head，请你反转链表，并返回反转后的链表。',
  },
  {
    id: '13',
    title: '岛屿数量',
    difficulty: 'medium',
    tags: ['数组', '深度优先搜索', '广度优先搜索', '并查集'],
    acceptanceRate: 0.52,
    totalSubmissions: 16500,
    description: '给你一个由 1（陆地）和 0（水）组成的的二维网格，请你计算网格中岛屿的数量。',
  },
  {
    id: '14',
    title: '正则表达式匹配',
    difficulty: 'hard',
    tags: ['字符串', '动态规划', '递归'],
    acceptanceRate: 0.15,
    totalSubmissions: 7600,
    description: '给你一个字符串 s 和一个字符规律 p，请你来实现一个支持 . 和 * 的正则表达式匹配。',
  },
  {
    id: '15',
    title: '爬楼梯',
    difficulty: 'easy',
    tags: ['动态规划', '记忆化搜索'],
    acceptanceRate: 0.73,
    totalSubmissions: 19800,
    description: '假设你正在爬楼梯。需要 n 阶你才能到达楼顶。每次你可以爬 1 或 2 个台阶。你有多少种不同的方法可以爬到楼顶呢？',
  },
]

export const allTags = Array.from(new Set(problems.flatMap(p => p.tags)))

export const difficultyConfig = {
  easy: { label: '简单', color: 'bg-green-100 text-green-700' },
  medium: { label: '中等', color: 'bg-yellow-100 text-yellow-700' },
  hard: { label: '困难', color: 'bg-red-100 text-red-700' },
}
