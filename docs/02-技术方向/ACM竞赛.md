# ACM 竞赛

ACM-ICPC（International Collegiate Programming Contest）是全球规模最大的大学生算法竞赛，与 CTF 是信息安全专业最常见的两类竞赛。ACM 考察的是**算法设计与实现能力**：给定一道题目，在规定时间内写出正确且高效的程序。

---

## 竞赛形式

- **组队**：3 人一组，共用一台电脑
- **语言**：C++（主流）、Java、Python
- **赛制**：5 小时，解出尽可能多的题目；通过数量相同时，用时少者排名靠前
- **层级**：校赛 → 区域赛（ICPC Regional）→ 全国邀请赛 → 世界总决赛（ICPC World Finals）
- **国内选拔**：CCPC（中国大学生程序设计竞赛）与 ICPC 并列为最重要的区域赛体系

---

## 学习路径

### 起点：会写代码就能入门

ACM 的门槛是能用 C++ 或 Java 实现基本逻辑，不需要任何安全背景。信息安全专业的同学通常在大一下学期开始。

### 推荐路线

```
基础语法 → 基础数据结构 → 基础算法 → 图论 → 动态规划 → 高级专题
（1~2月）    （1~2月）      （2~3月）   （3~4月）  （3~4月）    （持续深入）
```

**第一阶段**（打基础）

- 掌握 STL 容器：`vector`、`map`、`set`、`priority_queue`
- 排序、二分查找、前缀和、差分
- 字符串基础操作

**第二阶段**（核心算法）

- 图论：BFS/DFS、最短路（Dijkstra / SPFA）、最小生成树（Kruskal）
- 动态规划：背包、最长公共子序列、区间 DP
- 数论：GCD、快速幂、质数筛

**第三阶段**（进阶专题）

- 数据结构：线段树、树状数组、并查集
- 图论进阶：拓扑排序、网络流
- 字符串：KMP、Trie、AC自动机

---

## 练习平台

| 平台 | 特点 |
|---|---|
| [![Codeforces](https://img.shields.io/badge/Codeforces-codeforces.com-1F8ACB?style=plastic&logo=codeforces&logoColor=white)](https://codeforces.com) | 全球最活跃的竞赛平台，每周有比赛，题目质量高，**优先推荐** |
| [![洛谷](https://img.shields.io/badge/洛谷-luogu.com.cn-FE4C61?style=plastic)](https://www.luogu.com.cn) | 国内最友好的入门平台，题解丰富，中文界面 |
| [![AtCoder](https://img.shields.io/badge/AtCoder-atcoder.jp-222222?style=plastic)](https://atcoder.jp) | 日本平台，题目风格精致，数学味重 |
| [![POJ](https://img.shields.io/badge/POJ-poj.org-003399?style=plastic)](http://poj.org) | 北大 OJ，经典题库，历史悠久 |
| [![LeetCode](https://img.shields.io/badge/LeetCode-leetcode.cn-FFA116?style=plastic&logo=leetcode&logoColor=white)](https://leetcode.cn) | 面试导向，难度偏低，适合热身 |

---

## 核心知识点速览

=== "数据结构"

    - 栈、队列、双端队列
    - 堆（优先队列）
    - 并查集（Union-Find）
    - 线段树、树状数组（BIT）
    - Trie 字典树

=== "图论"

    - BFS / DFS 遍历
    - 最短路：Dijkstra（单源）、Floyd（全源）、SPFA
    - 最小生成树：Kruskal、Prim
    - 拓扑排序
    - 强连通分量（Tarjan）

=== "动态规划"

    - 线性 DP：最长上升子序列（LIS）、最长公共子序列（LCS）
    - 背包：0/1 背包、完全背包、分组背包
    - 区间 DP、树形 DP
    - 状压 DP

=== "数学"

    - 快速幂、矩阵快速幂
    - 质数筛（埃筛、线性筛）
    - GCD / LCM、扩展欧几里得
    - 组合数学、逆元

=== "字符串"

    - KMP 模式匹配
    - Manacher（最长回文子串）
    - 字符串哈希
    - AC 自动机

---

## 推荐资源

| 资源 | 说明 |
|---|---|
| [![北印ACM实验室](https://img.shields.io/badge/北印ACM实验室-bigcacm.pages.dev-0078D4?style=plastic)](https://bigcacm.pages.dev/quickstart/) | **学校 ACM 实验室官方入门指南**，从零开始，适合本校同学直接参考 |
| [OI Wiki](https://oi-wiki.org) | 国内最完整的算法竞赛知识库，中文，覆盖所有主题 |
| [算法竞赛入门经典（刘汝佳）](https://book.douban.com/subject/25902584/) | 经典教材，俗称"紫书" |
| [Codeforces 题单](https://codeforces.com/problemset) | 按 rating 刷题，从 800 分开始 |
| [洛谷题单广场](https://www.luogu.com.cn/training/list) | 按专题刷题，适合系统训练 |

!!! tip "刷题建议"
    Codeforces 按 rating 从低到高刷，每道题尽力独立思考 30 分钟，再看题解。看懂后一定要自己重新实现一遍。积累 200+ 题后，参加 Div.2 正式比赛，实战才是进步最快的方式。
