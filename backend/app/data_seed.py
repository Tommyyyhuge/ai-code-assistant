"""
知识图谱种子数据：20 个算法竞赛核心知识点

运行: conda run -n ai_code_assistant_env python -m app.data_seed
"""
import asyncio
from app.database import AsyncSessionLocal
from app.models.knowledge import KnowledgeNode, KnowledgeEdge

SEED_NODES = [
    {
        "title": "时间复杂度分析",
        "title_slug": "time-complexity",
        "path": "basics.time_complexity",
        "category": "基础",
        "level": 1,
        "order_index": 1,
        "estimated_minutes": 30,
        "description": "时间复杂度是衡量算法运行时间随输入规模增长的量度，通常用大 O 符号（Big-O Notation）表示。它是算法分析的核心工具，帮助我们比较不同算法在理论上的性能优劣。",
        "core_concept": "大 O 表示法描述的是算法运行时间的上界，关注的是输入规模 n 趋于无穷大时的增长趋势。常见复杂度从低到高：O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ) < O(n!)。常数项和低阶项在大 O 中被忽略，因为它们对大规模数据的增长贡献微乎其微。",
        "code_template_cpp": "// 分析循环的时间复杂度\nfor (int i = 0; i < n; i++) {        // O(n)\n    for (int j = 0; j < n; j++) {    // O(n²)\n        // 常数时间操作\n    }\n}",
        "code_template_py": "# 分析循环的时间复杂度\nfor i in range(n):          # O(n)\n    for j in range(n):      # O(n²)\n        pass  # 常数时间操作",
        "time_complexity": "O(1) ~ O(n!)",
        "common_mistakes": "1. 混淆最坏情况和平均情况\n2. 忽略递归调用的时间开销\n3. 认为两层循环一定是 O(n²)——要分析内层循环次数是否和 n 有关",
    },
    {
        "title": "冒泡排序",
        "title_slug": "bubble-sort",
        "path": "sorting.bubble",
        "category": "排序",
        "level": 1,
        "order_index": 1,
        "estimated_minutes": 20,
        "description": "冒泡排序通过重复遍历数列，依次比较相邻元素并交换逆序对，每一轮将最大的未排序元素'冒泡'到末尾。",
        "core_concept": "相邻比较 + 交换。每轮遍历后最大的元素到达正确位置，因此内循环可逐轮缩短。可通过设置 flag 检测本轮是否有交换来提前终止已有序的情况。",
        "algorithm_steps": "1. 从第一个元素开始，比较相邻的两个元素\n2. 如果顺序不对（前者大于后者），交换它们\n3. 对每一对相邻元素重复，直到数组末尾\n4. 重复步骤 1-3，每次遍历后减少已排序末尾的长度\n5. 如果某轮没有发生任何交换，提前结束",
        "code_template_cpp": "void bubbleSort(vector<int>& arr) {\n    int n = arr.size();\n    for (int i = 0; i < n - 1; i++) {\n        bool swapped = false;\n        for (int j = 0; j < n - 1 - i; j++) {\n            if (arr[j] > arr[j + 1]) {\n                swap(arr[j], arr[j + 1]);\n                swapped = true;\n            }\n        }\n        if (!swapped) break;\n    }\n}",
        "code_template_py": "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n - 1):\n        swapped = False\n        for j in range(n - 1 - i):\n            if arr[j] > arr[j + 1]:\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n                swapped = True\n        if not swapped:\n            break\n    return arr",
        "time_complexity": "O(n²) 最坏/平均, O(n) 最好",
        "space_complexity": "O(1)",
        "common_mistakes": "1. 内循环边界写成 n-1 而不是 n-1-i\n2. 忘记 break 优化，最坏情况退化为纯 O(n²)",
    },
    {
        "title": "选择排序",
        "title_slug": "selection-sort",
        "path": "sorting.selection",
        "category": "排序",
        "level": 1,
        "order_index": 2,
        "estimated_minutes": 15,
        "description": "选择排序每次从未排序区间选出最小元素，放到已排序区间的末尾。",
        "core_concept": "分区思想：维护已排序前缀和未排序后缀。每一轮在未排序后缀中找到最小值，与后缀的第一个元素交换。交换次数为 n-1，比较次数为 n(n-1)/2。",
        "code_template_cpp": "void selectionSort(vector<int>& arr) {\n    int n = arr.size();\n    for (int i = 0; i < n - 1; i++) {\n        int minIdx = i;\n        for (int j = i + 1; j < n; j++) {\n            if (arr[j] < arr[minIdx]) minIdx = j;\n        }\n        swap(arr[i], arr[minIdx]);\n    }\n}",
        "code_template_py": "def selection_sort(arr):\n    n = len(arr)\n    for i in range(n - 1):\n        min_idx = i\n        for j in range(i + 1, n):\n            if arr[j] < arr[min_idx]:\n                min_idx = j\n        arr[i], arr[min_idx] = arr[min_idx], arr[i]\n    return arr",
        "time_complexity": "O(n²)",
        "space_complexity": "O(1)",
        "common_mistakes": "1. 混淆选择排序和冒泡排序——选择排序是找最小值再交换，不是相邻交换\n2. 认为选择排序是稳定排序（实际上不是）",
    },
    {
        "title": "插入排序",
        "title_slug": "insertion-sort",
        "path": "sorting.insertion",
        "category": "排序",
        "level": 1,
        "order_index": 3,
        "estimated_minutes": 15,
        "description": "插入排序将数组分为已排序和未排序两部分，每次取未排序的第一个元素，在已排序部分中找到正确位置插入。",
        "core_concept": "类似整理扑克牌：每次拿一张新牌，从右向左在已排序的牌中找位置插入。算法稳定，对小规模数据或基本有序的数据效率极高。",
        "algorithm_steps": "1. 从第二个元素开始，认为第一个元素已排序\n2. 取出当前元素 key\n3. 从 key 的前一个位置向左扫描\n4. 如果扫描元素大于 key，将其右移一位\n5. 将 key 插入正确位置",
        "code_template_cpp": "void insertionSort(vector<int>& arr) {\n    int n = arr.size();\n    for (int i = 1; i < n; i++) {\n        int key = arr[i];\n        int j = i - 1;\n        while (j >= 0 && arr[j] > key) {\n            arr[j + 1] = arr[j];\n            j--;\n        }\n        arr[j + 1] = key;\n    }\n}",
        "code_template_py": "def insertion_sort(arr):\n    for i in range(1, len(arr)):\n        key = arr[i]\n        j = i - 1\n        while j >= 0 and arr[j] > key:\n            arr[j + 1] = arr[j]\n            j -= 1\n        arr[j + 1] = key\n    return arr",
        "time_complexity": "O(n²) 最坏, O(n) 最好",
        "space_complexity": "O(1)",
        "common_mistakes": "1. while 循环条件写成 arr[j] >= key 会导致不稳定排序\n2. 忘记 j >= 0 边界检查",
    },
    {
        "title": "快速排序",
        "title_slug": "quick-sort",
        "path": "sorting.quick",
        "category": "排序",
        "level": 2,
        "order_index": 4,
        "estimated_minutes": 30,
        "description": "快速排序采用分治策略，选择一个基准(pivot)元素，将数组划分为小于和大于基准的两部分，递归排序子数组。",
        "core_concept": "划分(partition)是核心。将小于 pivot 的放左边，大于的放右边，pivot 放到最终位置。递归深度决定了性能——随机选取或三数取中 pivot 避免退化。",
        "code_template_cpp": "int partition(vector<int>& arr, int low, int high) {\n    int pivot = arr[high];\n    int i = low - 1;\n    for (int j = low; j < high; j++) {\n        if (arr[j] <= pivot) swap(arr[++i], arr[j]);\n    }\n    swap(arr[i + 1], arr[high]);\n    return i + 1;\n}\n\nvoid quickSort(vector<int>& arr, int low, int high) {\n    if (low < high) {\n        int pi = partition(arr, low, high);\n        quickSort(arr, low, pi - 1);\n        quickSort(arr, pi + 1, high);\n    }\n}",
        "code_template_py": "def quick_sort(arr, low, high):\n    if low < high:\n        pi = partition(arr, low, high)\n        quick_sort(arr, low, pi - 1)\n        quick_sort(arr, pi + 1, high)\n\ndef partition(arr, low, high):\n    pivot = arr[high]\n    i = low - 1\n    for j in range(low, high):\n        if arr[j] <= pivot:\n            i += 1\n            arr[i], arr[j] = arr[j], arr[i]\n    arr[i + 1], arr[high] = arr[high], arr[i + 1]\n    return i + 1",
        "time_complexity": "O(n log n) 平均, O(n²) 最坏",
        "space_complexity": "O(log n) 递归栈",
        "common_mistakes": "1. 选第一个或最后一个元素作为 pivot 在已排序数组上退化为 O(n²)\n2. partition 实现中索引边界错误",
    },
    {
        "title": "归并排序",
        "title_slug": "merge-sort",
        "path": "sorting.merge",
        "category": "排序",
        "level": 2,
        "order_index": 5,
        "estimated_minutes": 25,
        "description": "归并排序是经典的分治算法，将数组递归地分成两半，分别排序后合并。它是稳定排序，任何情况下都是 O(n log n)。",
        "core_concept": "分(divide): 递归将数组对半分割直到长度为 1。治(conquer): 合并两个有序子数组，使用双指针比较法。需要 O(n) 额外空间存储合并结果。",
        "algorithm_steps": "1. 找到数组中间位置 mid = (left + right) / 2\n2. 递归排序左半部分 mergeSort(arr, left, mid)\n3. 递归排序右半部分 mergeSort(arr, mid+1, right)\n4. 合并两个有序子数组 merge(arr, left, mid, right)",
        "code_template_cpp": "void merge(vector<int>& arr, int l, int m, int r) {\n    vector<int> L(arr.begin()+l, arr.begin()+m+1);\n    vector<int> R(arr.begin()+m+1, arr.begin()+r+1);\n    int i = 0, j = 0, k = l;\n    while (i < L.size() && j < R.size())\n        arr[k++] = (L[i] <= R[j]) ? L[i++] : R[j++];\n    while (i < L.size()) arr[k++] = L[i++];\n    while (j < R.size()) arr[k++] = R[j++];\n}\n\nvoid mergeSort(vector<int>& arr, int l, int r) {\n    if (l < r) {\n        int m = l + (r - l) / 2;\n        mergeSort(arr, l, m);\n        mergeSort(arr, m + 1, r);\n        merge(arr, l, m, r);\n    }\n}",
        "code_template_py": "def merge_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    mid = len(arr) // 2\n    left = merge_sort(arr[:mid])\n    right = merge_sort(arr[mid:])\n    return merge(left, right)\n\ndef merge(left, right):\n    result = []\n    i = j = 0\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            result.append(left[i]); i += 1\n        else:\n            result.append(right[j]); j += 1\n    result.extend(left[i:])\n    result.extend(right[j:])\n    return result",
        "time_complexity": "O(n log n)",
        "space_complexity": "O(n)",
        "common_mistakes": "1. 忘记处理剩余元素（L 或 R 中的一个可能还有剩余）\n2. 用切片创建子数组时忽略索引边界",
    },
    {
        "title": "二分查找",
        "title_slug": "binary-search",
        "path": "searching.binary",
        "category": "搜索",
        "level": 2,
        "order_index": 1,
        "estimated_minutes": 25,
        "description": "二分查找在有序数组中通过反复折半来定位目标值。每次将搜索范围缩小一半，是时间复杂度最低的查找算法。",
        "core_concept": "维护 [left, right] 搜索区间（闭区间）。每次取中间元素与目标比较，如果相等则返回，如果目标小于中间元素则在左半继续，否则在右半继续。二分查找也可以用于查找插入位置（lower_bound/upper_bound）。",
        "algorithm_steps": "1. 初始化 left=0, right=n-1\n2. 当 left <= right 时循环\n3. 计算 mid = left + (right-left)/2（防溢出）\n4. 如果 arr[mid]==target，返回 mid\n5. 如果 arr[mid] > target，right = mid-1\n6. 如果 arr[mid] < target，left = mid+1\n7. 未找到返回 -1",
        "code_template_cpp": "int binarySearch(vector<int>& arr, int target) {\n    int left = 0, right = arr.size() - 1;\n    while (left <= right) {\n        int mid = left + (right - left) / 2;\n        if (arr[mid] == target) return mid;\n        else if (arr[mid] > target) right = mid - 1;\n        else left = mid + 1;\n    }\n    return -1;\n}",
        "code_template_py": "def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = left + (right - left) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] > target:\n            right = mid - 1\n        else:\n            left = mid + 1\n    return -1",
        "time_complexity": "O(log n)",
        "space_complexity": "O(1)",
        "common_mistakes": "1. mid 用 (left+right)/2 可能溢出\n2. 循环条件写成 left < right 会漏掉最后一个元素\n3. 左右边界更新写成 mid 而不是 mid±1 导致死循环",
    },
    {
        "title": "深度优先搜索 (DFS)",
        "title_slug": "dfs",
        "path": "searching.dfs",
        "category": "搜索",
        "level": 2,
        "order_index": 2,
        "estimated_minutes": 30,
        "description": "深度优先搜索从起点出发，沿着一条路径走到尽头，然后回溯探索其他分支。DFS 天然适用于递归实现，是回溯算法和图遍历的基础。",
        "core_concept": "DFS 可以用递归（系统栈）或显式栈实现。核心思想：标记已访问节点，逐个探索未访问的邻居。在图遍历中，DFS 可以判断连通性、寻找路径、拓扑排序、检测环。",
        "code_template_cpp": "void dfs(vector<vector<int>>& graph, int node, vector<bool>& visited) {\n    visited[node] = true;\n    for (int neighbor : graph[node]) {\n        if (!visited[neighbor])\n            dfs(graph, neighbor, visited);\n    }\n}",
        "code_template_py": "def dfs(graph, node, visited):\n    visited[node] = True\n    for neighbor in graph[node]:\n        if not visited[neighbor]:\n            dfs(graph, neighbor, visited)",
        "time_complexity": "O(V + E)",
        "space_complexity": "O(V)",
        "common_mistakes": "1. 忘记标记 visited 导致无限递归\n2. Python 递归深度 1000 限制——大量节点需用迭代栈或用 sys.setrecursionlimit\n3. 非连通图需要外层循环遍历所有节点",
    },
    {
        "title": "广度优先搜索 (BFS)",
        "title_slug": "bfs",
        "path": "searching.bfs",
        "category": "搜索",
        "level": 2,
        "order_index": 3,
        "estimated_minutes": 25,
        "description": "广度优先搜索从起点出发，层层向外扩展。BFS 是求无权图最短路径的标准算法，也广泛用于二叉树的层序遍历。",
        "core_concept": "BFS 使用队列(queue)逐层处理。先将起点入队，然后每次出队一个节点并把它所有未访问的邻居入队。BFS 保证首次访问某节点时经过的边数是最少的。",
        "algorithm_steps": "1. 初始化队列，将起点入队并标记已访问\n2. 当队列非空时循环\n3. 出队当前节点，处理它\n4. 遍历当前节点的所有邻居\n5. 未访问的邻居入队并标记\n6. 重复直到队列为空",
        "code_template_cpp": "void bfs(vector<vector<int>>& graph, int start) {\n    queue<int> q;\n    vector<bool> visited(graph.size(), false);\n    q.push(start);\n    visited[start] = true;\n    while (!q.empty()) {\n        int node = q.front(); q.pop();\n        for (int neighbor : graph[node]) {\n            if (!visited[neighbor]) {\n                visited[neighbor] = true;\n                q.push(neighbor);\n            }\n        }\n    }\n}",
        "code_template_py": "from collections import deque\n\ndef bfs(graph, start):\n    visited = [False] * len(graph)\n    q = deque([start])\n    visited[start] = True\n    while q:\n        node = q.popleft()\n        for neighbor in graph[node]:\n            if not visited[neighbor]:\n                visited[neighbor] = True\n                q.append(neighbor)",
        "time_complexity": "O(V + E)",
        "space_complexity": "O(V)",
        "common_mistakes": "1. 忘记在入队时标记 visited（而非出队时）——会导致重复入队，复杂度退化\n2. 用 list 作为队列（pop(0) 是 O(n)），应使用 deque",
    },
    {
        "title": "栈与队列",
        "title_slug": "stack-queue",
        "path": "data_structures.stack_queue",
        "category": "数据结构",
        "level": 1,
        "order_index": 1,
        "estimated_minutes": 20,
        "description": "栈是后进先出(LIFO)的线性结构，队列是先进先出(FIFO)的线性结构。它们是实现 DFS、BFS、表达式求值、括号匹配等算法的基础。",
        "core_concept": "栈：push/pop/top 操作均为 O(1)。应用：递归模拟、括号匹配、单调栈求下一个更大元素。队列：enqueue/dequeue/front 操作 O(1)。应用：BFS、滑动窗口、生产者消费者模型。",
        "code_template_cpp": "// 栈\nstack<int> stk;\nstk.push(1); stk.pop(); int top = stk.top();\n\n// 队列\nqueue<int> q;\nq.push(1); q.pop(); int front = q.front();",
        "code_template_py": "# 栈（直接用 list）\nstack = []\nstack.append(1)  # push\nstack.pop()      # pop\nstack[-1]        # top\n\n# 队列\nfrom collections import deque\nq = deque()\nq.append(1)      # enqueue\nq.popleft()      # dequeue\nq[0]             # front",
        "time_complexity": "O(1) 所有基本操作",
        "space_complexity": "O(n)",
        "common_mistakes": "1. Python 用 list 做队列导致 O(n) 出队\n2. pop 前不检查 empty 导致异常\n3. 混淆 LIFO 和 FIFO",
    },
    {
        "title": "链表",
        "title_slug": "linked-list",
        "path": "data_structures.linked_list",
        "category": "数据结构",
        "level": 1,
        "order_index": 2,
        "estimated_minutes": 25,
        "description": "链表是由节点组成的线性结构，每个节点包含数据和指向下一个节点的指针。链表支持 O(1) 的头部插入/删除，但随机访问需要 O(n)。",
        "core_concept": "单链表：node → node → null。双链表：prev ← node → next。与数组相比：链表不需要连续内存，插入删除高效，但无法随机访问。常考题型：反转链表、快慢指针找中点、检测环。",
        "code_template_cpp": "struct ListNode {\n    int val;\n    ListNode* next;\n    ListNode(int x) : val(x), next(nullptr) {}\n};\n\nListNode* reverseList(ListNode* head) {\n    ListNode *prev = nullptr, *curr = head;\n    while (curr) {\n        ListNode* next = curr->next;\n        curr->next = prev;\n        prev = curr;\n        curr = next;\n    }\n    return prev;\n}",
        "code_template_py": "class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef reverse_list(head):\n    prev, curr = None, head\n    while curr:\n        next_node = curr.next\n        curr.next = prev\n        prev = curr\n        curr = next_node\n    return prev",
        "time_complexity": "O(n) 遍历, O(1) 插入/删除",
        "space_complexity": "O(n)",
        "common_mistakes": "1. 反转链表时丢失 next 指针\n2. 忘记处理空链表和单节点边界\n3. 循环检测用快慢指针时条件写错",
    },
    {
        "title": "二叉树",
        "title_slug": "binary-tree",
        "path": "data_structures.binary_tree",
        "category": "数据结构",
        "level": 2,
        "order_index": 3,
        "estimated_minutes": 30,
        "description": "二叉树每个节点最多有两个子节点（左和右）。二叉搜索树(BST)是左<根<右的特殊二叉树，支持 O(log n) 的查找、插入、删除。二叉堆是完全二叉树，用于优先队列。",
        "core_concept": "遍历方式：前序(根左右)、中序(左根右)、后序(左右根)、层序。BST 的中序遍历即是有序序列。平衡二叉树(AVL、红黑树)通过旋转操作保证树的高度为 O(log n)。",
        "code_template_cpp": "struct TreeNode {\n    int val;\n    TreeNode *left, *right;\n    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}\n};\n\nvoid inorder(TreeNode* root) {\n    if (!root) return;\n    inorder(root->left);\n    cout << root->val;\n    inorder(root->right);\n}",
        "code_template_py": "class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef inorder(root):\n    if not root:\n        return\n    inorder(root.left)\n    print(root.val)\n    inorder(root.right)",
        "time_complexity": "O(log n) BST 操作, O(n) 遍历",
        "space_complexity": "O(n)",
        "common_mistakes": "1. 递归忘了 base case 导致栈溢出\n2. BST 删除节点时有左右子树都存在的复杂情况\n3. 混淆完全二叉树和满二叉树的定义",
    },
    {
        "title": "哈希表",
        "title_slug": "hash-table",
        "path": "data_structures.hash_table",
        "category": "数据结构",
        "level": 2,
        "order_index": 4,
        "estimated_minutes": 20,
        "description": "哈希表通过哈希函数将键映射到存储桶，支持 O(1) 平均时间的查找、插入、删除。是两数之和、字符统计、去重、缓存等问题的首选数据结构。",
        "core_concept": "哈希函数：key → 桶索引。解决冲突：链地址法(桶内链表)或开放地址法(线性探测)。Python 的 dict/set 和 C++ 的 unordered_map/unordered_set 都是哈希表实现。",
        "code_template_cpp": "unordered_map<int, int> freq;\nfor (int x : nums) freq[x]++;\nif (freq.count(target)) return freq[target];",
        "code_template_py": "freq = {}\nfor x in nums:\n    freq[x] = freq.get(x, 0) + 1\nif target in freq:\n    return freq[target]",
        "time_complexity": "O(1) 平均, O(n) 最坏",
        "space_complexity": "O(n)",
        "common_mistakes": "1. 认为哈希表一定比数组快——n 小时数组直接索引更优\n2. Python 用可变对象（如 list）作为 dict key\n3. 哈希冲突导致的性能退化",
    },
    {
        "title": "动态规划入门",
        "title_slug": "dp-intro",
        "path": "dp.intro",
        "category": "动态规划",
        "level": 3,
        "order_index": 1,
        "estimated_minutes": 40,
        "description": "动态规划通过将问题分解为重叠子问题，并存储子问题的解来避免重复计算。DP 的核心是找到状态定义和状态转移方程。",
        "core_concept": "DP 两个要素：最优子结构（大问题的最优解包含子问题的最优解）和重叠子问题（子问题被反复计算）。实现方式：自顶向下（记忆化搜索）或自底向上（填表）。以斐波那契数列为例，f(n) = f(n-1) + f(n-2)，用 dp[i] 存 f(i)。",
        "algorithm_steps": "1. 定义状态：dp[i] 表示什么\n2. 找转移方程：dp[i] = f(dp[i-1], dp[i-2], ...)\n3. 初始化边界：dp[0], dp[1] 等基础值\n4. 确定遍历顺序：如何保证子问题先于当前问题计算\n5. 返回目标状态",
        "code_template_cpp": "// 爬楼梯: 每次爬 1 或 2 阶，n 阶有多少种方法\nint climbStairs(int n) {\n    vector<int> dp(n + 1, 0);\n    dp[0] = 1; dp[1] = 1;\n    for (int i = 2; i <= n; i++)\n        dp[i] = dp[i - 1] + dp[i - 2];\n    return dp[n];\n}",
        "code_template_py": "def climb_stairs(n):\n    dp = [0] * (n + 1)\n    dp[0] = dp[1] = 1\n    for i in range(2, n + 1):\n        dp[i] = dp[i - 1] + dp[i - 2]\n    return dp[n]",
        "time_complexity": "O(n)",
        "space_complexity": "O(n), 可优化为 O(1)",
        "common_mistakes": "1. 混淆 DP 和贪心——DP 考虑所有可能，贪心只选局部最优\n2. 忘记初始化 dp[0]，导致索引越界\n3. 转移方程写错方向",
    },
    {
        "title": "背包问题",
        "title_slug": "knapsack",
        "path": "dp.knapsack",
        "category": "动态规划",
        "level": 3,
        "order_index": 2,
        "estimated_minutes": 35,
        "description": "背包问题是 DP 的经典模型。0-1 背包：N 件物品每件只能选或不选，容量 W 的背包能装的最大价值是多少。",
        "core_concept": "状态：dp[i][w] = 前 i 件物品，容量 w 时的最大价值。转移：dp[i][w] = max(dp[i-1][w], dp[i-1][w-wt[i]] + val[i])。空间可优化为一维：dp[w] = max(dp[w], dp[w-wt[i]] + val[i])，但必须**倒序**遍历 w 避免物品被重复选取。",
        "algorithm_steps": "1. 初始化 dp[0..W] = 0\n2. 遍历每件物品 i\n3. 倒序遍历容量 w 从 W 到 wt[i]\n4. dp[w] = max(dp[w], dp[w-wt[i]] + val[i])\n5. 答案 = dp[W]",
        "code_template_cpp": "int knapsack(vector<int>& wt, vector<int>& val, int W) {\n    vector<int> dp(W + 1, 0);\n    for (int i = 0; i < wt.size(); i++)\n        for (int w = W; w >= wt[i]; w--)\n            dp[w] = max(dp[w], dp[w - wt[i]] + val[i]);\n    return dp[W];\n}",
        "code_template_py": "def knapsack(wt, val, W):\n    dp = [0] * (W + 1)\n    for i in range(len(wt)):\n        for w in range(W, wt[i] - 1, -1):  # 倒序遍历\n            dp[w] = max(dp[w], dp[w - wt[i]] + val[i])\n    return dp[W]",
        "time_complexity": "O(N*W)",
        "space_complexity": "O(W)",
        "common_mistakes": "1. 一维优化时正序遍历导致完全背包（物品可无限选）\n2. 二维写法时忘记 dp[i][w] = dp[i-1][w] 的继承\n3. W 很大时 MLE——完全背包用贪心预处理",
    },
    {
        "title": "最长公共子序列 (LCS)",
        "title_slug": "lcs",
        "path": "dp.lcs",
        "category": "动态规划",
        "level": 3,
        "order_index": 3,
        "estimated_minutes": 25,
        "description": "求两个序列的最长公共子序列（不要求连续）。LCS 是经典的字符串 DP 问题，也是编辑距离等算法的基础。",
        "core_concept": "状态：dp[i][j] = text1[0..i] 和 text2[0..j] 的 LCS 长度。转移：如果 text1[i]==text2[j]，dp[i][j] = dp[i-1][j-1] + 1；否则 dp[i][j] = max(dp[i-1][j], dp[i][j-1])。",
        "code_template_cpp": "int longestCommonSubsequence(string a, string b) {\n    int m = a.size(), n = b.size();\n    vector<vector<int>> dp(m + 1, vector<int>(n + 1, 0));\n    for (int i = 1; i <= m; i++)\n        for (int j = 1; j <= n; j++)\n            if (a[i-1] == b[j-1])\n                dp[i][j] = dp[i-1][j-1] + 1;\n            else\n                dp[i][j] = max(dp[i-1][j], dp[i][j-1]);\n    return dp[m][n];\n}",
        "code_template_py": "def lcs(a, b):\n    m, n = len(a), len(b)\n    dp = [[0] * (n + 1) for _ in range(m + 1)]\n    for i in range(1, m + 1):\n        for j in range(1, n + 1):\n            if a[i-1] == b[j-1]:\n                dp[i][j] = dp[i-1][j-1] + 1\n            else:\n                dp[i][j] = max(dp[i-1][j], dp[i][j-1])\n    return dp[m][n]",
        "time_complexity": "O(m*n)",
        "space_complexity": "O(m*n), 可优化为 O(min(m,n))",
        "common_mistakes": "1. 混淆子序列和子串——子序列不要求连续\n2. 索引偏移：dp[i][j] 对应 text1[i-1] 和 text2[j-1]\n3. 背包和 LCS 的遍历方向混淆",
    },
    {
        "title": "贪心算法基础",
        "title_slug": "greedy-intro",
        "path": "greedy.intro",
        "category": "贪心",
        "level": 2,
        "order_index": 1,
        "estimated_minutes": 25,
        "description": "贪心算法在每一步都做出当前看起来最优的选择，不考虑未来的影响。适用于具有贪心选择性质和最优子结构的问题。",
        "core_concept": "贪心 vs DP：贪心每步选当前最优，不会回头；DP 会考虑所有可能。贪心需要证明正确性——通常用反证法或数学归纳法。经典贪心问题：找零钱（硬币系统规范时）、活动选择、霍夫曼编码。",
        "code_template_cpp": "// 活动选择: 选择最多的不冲突活动\nint maxActivities(vector<pair<int,int>>& acts) {\n    sort(acts.begin(), acts.end(),\n         [](auto& a, auto& b) { return a.second < b.second; });\n    int count = 1, last_end = acts[0].second;\n    for (int i = 1; i < acts.size(); i++) {\n        if (acts[i].first >= last_end) {\n            count++;\n            last_end = acts[i].second;\n        }\n    }\n    return count;\n}",
        "code_template_py": "def max_activities(activities):\n    activities.sort(key=lambda x: x[1])  # 按结束时间排序\n    count = 1\n    last_end = activities[0][1]\n    for start, end in activities[1:]:\n        if start >= last_end:\n            count += 1\n            last_end = end\n    return count",
        "time_complexity": "O(n log n)（排序主导）",
        "space_complexity": "O(1)",
        "common_mistakes": "1. 没有严格证明贪心选择性质就直接使用\n2. 排序键选择错误——活动选择应按结束时间而非开始时间\n3. 混淆贪心和 DP 的适用场景",
    },
    {
        "title": "区间调度",
        "title_slug": "interval-scheduling",
        "path": "greedy.interval",
        "category": "贪心",
        "level": 2,
        "order_index": 2,
        "estimated_minutes": 20,
        "description": "区间调度是贪心算法的经典应用场景，包括选择最多不重叠区间、合并重叠区间、用最少的点覆盖所有区间等变体。",
        "core_concept": "关键策略：按区间右端点升序排列，贪心选择最早结束的区间。这个策略保证了剩余可用的时间最多，从而能容纳更多的后续区间。",
        "code_template_cpp": "// 合并重叠区间\nvector<vector<int>> merge(vector<vector<int>>& intervals) {\n    sort(intervals.begin(), intervals.end());\n    vector<vector<int>> res;\n    for (auto& iv : intervals) {\n        if (res.empty() || res.back()[1] < iv[0])\n            res.push_back(iv);\n        else\n            res.back()[1] = max(res.back()[1], iv[1]);\n    }\n    return res;\n}",
        "code_template_py": "def merge_intervals(intervals):\n    intervals.sort()\n    res = []\n    for iv in intervals:\n        if not res or res[-1][1] < iv[0]:\n            res.append(iv)\n        else:\n            res[-1][1] = max(res[-1][1], iv[1])\n    return res",
        "time_complexity": "O(n log n)",
        "space_complexity": "O(n)",
        "common_mistakes": "1. 合并区间忘记更新右端点为 max\n2. 不同变体用不同的排序键，不要混淆\n3. 区间调度变体多，每种贪心策略不同",
    },
    {
        "title": "最短路径 (Dijkstra)",
        "title_slug": "dijkstra",
        "path": "graph.dijkstra",
        "category": "图论",
        "level": 3,
        "order_index": 1,
        "estimated_minutes": 35,
        "description": "Dijkstra 算法求单源最短路径，适用于边权非负的图。它每次从尚未确定最短距离的节点中选择距离最小的，并更新其邻居的距离。",
        "core_concept": "贪心策略：维护 dist[] 数组和优先队列。每次从优先队列中弹出距离最小的节点，如果该距离大于已记录的距离则跳过，否则遍历其所有边进行松弛操作：if dist[v] > dist[u] + w: dist[v] = dist[u] + w。正确性依赖边权非负。",
        "algorithm_steps": "1. 初始化 dist[src]=0, 其他节点 dist=∞\n2. 将所有节点压入优先队列（或按需压入）\n3. 重复弹出距离最小节点 u\n4. 对于 u 的每条边 (u,v,w)，如果 dist[v] > dist[u] + w，则更新 dist[v] 并压入队列\n5. 队列为空时结束",
        "code_template_cpp": "vector<int> dijkstra(vector<vector<pair<int,int>>>& graph, int src) {\n    int n = graph.size();\n    vector<int> dist(n, INT_MAX);\n    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<>> pq;\n    dist[src] = 0;\n    pq.push({0, src});\n    while (!pq.empty()) {\n        auto [d, u] = pq.top(); pq.pop();\n        if (d > dist[u]) continue;\n        for (auto& [v, w] : graph[u]) {\n            if (dist[v] > dist[u] + w) {\n                dist[v] = dist[u] + w;\n                pq.push({dist[v], v});\n            }\n        }\n    }\n    return dist;\n}",
        "code_template_py": "import heapq\n\ndef dijkstra(graph, src):\n    n = len(graph)\n    dist = [float('inf')] * n\n    dist[src] = 0\n    pq = [(0, src)]\n    while pq:\n        d, u = heapq.heappop(pq)\n        if d > dist[u]:\n            continue\n        for v, w in graph[u]:\n            if dist[v] > dist[u] + w:\n                dist[v] = dist[u] + w\n                heapq.heappush(pq, (dist[v], v))\n    return dist",
        "time_complexity": "O((V+E) log V)",
        "space_complexity": "O(V)",
        "common_mistakes": "1. 优先队列中同一节点可能有多个距离记录——需检查 d > dist[u] 跳过旧记录\n2. 边权为负时 Dijkstra 失效，需用 Bellman-Ford 或 SPFA\n3. Priority queue 比较时用 > 而非 <（C++ 默认大根堆，需用 greater）",
    },
    {
        "title": "递归与分治",
        "title_slug": "recursion-divide-conquer",
        "path": "basics.recursion",
        "category": "基础",
        "level": 2,
        "order_index": 2,
        "estimated_minutes": 25,
        "description": "递归是函数调用自身来解决问题的编程技巧。分治是将大问题分解为若干个相同的小问题，分别解决后再合并。归并排序和快速排序是分治的经典例子。",
        "core_concept": "递归三要素：base case（终止条件）、recursive case（递推关系）、收敛保证（每次递归问题规模减小）。分治三步：分解(divide)、解决(conquer)、合并(combine)。递归的时间复杂度可用主定理(Master Theorem)分析。",
        "code_template_cpp": "// 快速幂: 计算 x^n，O(log n)\nlong long fastPow(long long x, int n) {\n    if (n == 0) return 1;\n    long long half = fastPow(x, n / 2);\n    return (n % 2 == 0) ? half * half : half * half * x;\n}",
        "code_template_py": "def fast_pow(x, n):\n    if n == 0:\n        return 1\n    half = fast_pow(x, n // 2)\n    return half * half if n % 2 == 0 else half * half * x",
        "time_complexity": "O(log n) 快速幂",
        "space_complexity": "O(log n) 递归栈",
        "common_mistakes": "1. 忘记 base case 导致无限递归\n2. 子问题规模没有减小\n3. 重复计算同一子问题（应用记忆化解决）",
    },
]

# 知识点之间的关联边
SEED_EDGES = [
    # 基础 → 排序
    ("time-complexity", "bubble-sort", "prerequisite"),
    ("recursion-divide-conquer", "quick-sort", "prerequisite"),
    ("recursion-divide-conquer", "merge-sort", "prerequisite"),
    # 排序链
    ("bubble-sort", "selection-sort", "next"),
    ("selection-sort", "insertion-sort", "next"),
    ("insertion-sort", "quick-sort", "next"),
    ("quick-sort", "merge-sort", "next"),
    # 搜索
    ("time-complexity", "binary-search", "prerequisite"),
    ("stack-queue", "dfs", "prerequisite"),
    ("stack-queue", "bfs", "prerequisite"),
    ("dfs", "bfs", "related"),
    ("binary-search", "dfs", "related"),
    # 数据结构
    ("stack-queue", "linked-list", "next"),
    ("linked-list", "binary-tree", "next"),
    ("binary-tree", "hash-table", "next"),
    # DP
    ("recursion-divide-conquer", "dp-intro", "prerequisite"),
    ("time-complexity", "dp-intro", "prerequisite"),
    ("dp-intro", "knapsack", "next"),
    ("dp-intro", "lcs", "next"),
    ("knapsack", "lcs", "related"),
    # 贪心
    ("dp-intro", "greedy-intro", "related"),
    ("greedy-intro", "interval-scheduling", "next"),
    # 图论
    ("dfs", "dijkstra", "prerequisite"),
    ("bfs", "dijkstra", "related"),
    ("greedy-intro", "dijkstra", "related"),
    # 搜索 → 数据结构
    ("dfs", "binary-tree", "related"),
    ("bfs", "binary-tree", "related"),
]


async def seed():
    from sqlalchemy import text as sa_text

    async with AsyncSessionLocal() as db:
        # 清理已有数据（幂等重跑）
        await db.execute(sa_text("DELETE FROM knowledge_edges"))
        await db.execute(sa_text("DELETE FROM knowledge_nodes"))
        await db.commit()
        print("已清空旧数据")

        # 插入节点（用 raw SQL 处理 ltree 列）

        def _build_insert(row: dict) -> tuple[str, dict]:
            """构建动态 INSERT，跳过值为 None 的列，id 用 gen_random_uuid()"""
            cols = ["id"] + [c for c in row if row[c] is not None]
            values = ["gen_random_uuid()"] + [f":{c}" for c in cols[1:]]
            sql = f"INSERT INTO knowledge_nodes ({', '.join(cols)}) VALUES ({', '.join(values)}) RETURNING id"
            return sql, {c: row[c] for c in cols if c != "id"}

        slug_map = {}
        for data in SEED_NODES:
            insert_data = {**data, "is_published": True}
            sql, params = _build_insert(insert_data)
            result = await db.execute(sa_text(sql), params)
            node_id = result.scalar_one()
            slug_map[data["title_slug"]] = node_id

        print(f"插入 {len(SEED_NODES)} 个知识点")

        # 插入边
        edge_count = 0
        for from_slug, to_slug, edge_type in SEED_EDGES:
            if from_slug in slug_map and to_slug in slug_map:
                await db.execute(
                    sa_text(
                        "INSERT INTO knowledge_edges (id, from_node_id, to_node_id, edge_type) "
                        "VALUES (gen_random_uuid(), :from_id, :to_id, :edge_type)"
                    ),
                    {"from_id": slug_map[from_slug], "to_id": slug_map[to_slug], "edge_type": edge_type},
                )
                edge_count += 1

        await db.commit()
        print(f"插入 {edge_count} 条关联边")
        print(f"[DONE] 知识图谱种子数据导入完成")


if __name__ == "__main__":
    asyncio.run(seed())
