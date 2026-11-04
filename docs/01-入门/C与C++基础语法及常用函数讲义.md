# C 与 C++ 基础语法及常用函数讲义

> 面向第一次系统过 C/C++ 语法的新生。课堂先运行程序，再改输入、预测输出、解释为什么；不要把 C 和 C++ 当成一套完全相同的语法。本文的每个标有文件名的代码块都可单独保存、编译。

## 今天的路线（约 90～120 分钟）

| 时间 | 内容 | 当场要做的事 |
|---|---|---|
| 0～15 分钟 | 程序结构、变量、输入输出与运算 | 运行第一个程序，改两个变量 |
| 15～35 分钟 | 判断、循环、函数、数组 | 手算一次循环，再对照输出 |
| 35～60 分钟 | C/C++ 两种字符串和常用函数 | 运行函数示例，解释参数与返回值 |
| 60～80 分钟 | 指针/引用、容器、算法 | 修改排序顺序，观察变量变化 |
| 80～120 分钟 | 常见错误与练习 | 独立完成一道题并互查 |

时间只有 90 分钟时，先讲前四段和练习 1；函数速查表留作课后查阅。**本课目标是会读、会改、会查，不是背完所有函数。**

## 一、先把程序跑起来

一个程序从 `main` 开始。`#include` 引入声明，花括号划分代码块，分号结束大多数语句。注释 `// ...` 不执行。C 源文件通常为 `.c`，C++ 通常为 `.cpp`；对应编译器和标准库不同。

在 PowerShell 中，进入保存文件的目录后运行：

```powershell
gcc -std=c11 -Wall -Wextra 01_c_basics.c -o 01_c_basics.exe
.\01_c_basics.exe
g++ -std=c++17 -Wall -Wextra 02_cpp_basics.cpp -o 02_cpp_basics.exe
.\02_cpp_basics.exe
```

若提示“找不到 gcc/g++”，先确认编译器是否安装，再检查 `Get-Command gcc`、`Get-Command g++` 和 PATH；这与源代码语法错误不是同一个问题。编译成功但运行结果不对，也不能说“编译器坏了”，应检查输入、计算过程和边界条件。

运行后面的示例时，把编译命令中的源文件名和输出文件名替换成对应编号；C 数学函数示例在 Linux 使用 GCC 链接时，还需把 `-lm` 放在命令末尾。

## 二、C 语法：从变量到函数

保存为 `01_c_basics.c`，运行时输入一个非负整数，例如 `5`。

```c
#include <stdio.h>

int sum_to(int n) {                // 函数：参数 n，返回 int
    int sum = 0;
    for (int i = 1; i <= n; ++i) {
        sum += i;                  // 等价于 sum = sum + i
    }
    return sum;
}

int main(void) {
    int n = 0;                    // 整数变量
    printf("请输入一个非负整数：");
    if (scanf("%d", &n) != 1 || n < 0) {
        puts("输入无效");
        return 1;                 // 非 0 通常表示出错
    }

    if (n % 2 == 0) {             // == 比较相等；% 求余
        puts("偶数");
    } else {
        puts("奇数");
    }

    int first_five[5] = {1, 2, 3, 4, 5};
    int total = 0;
    for (int i = 0; i < 5; ++i) { // 下标从 0 开始
        total += first_five[i];
    }

    printf("1 到 %d 的和：%d\n", n, sum_to(n));
    printf("数组前五项的和：%d\n", total);
    printf("整数除法 5 / 2 = %d\n", 5 / 2);
    printf("小数除法 5.0 / 2 = %.1f\n", 5.0 / 2);
    return 0;
}
```

输入 `5` 时，应看到“奇数”、`1 到 5 的和：15`、`数组前五项的和：15`、`5 / 2 = 2`、`5.0 / 2 = 2.5`。让学生先手算 `sum` 依次变成多少（1、3、6、10、15），再运行。

**逐句说明：**

- `int` 是整数；`double` 常用于带小数的计算；`char` 表示字符。类型决定数据如何表示和可做的运算。`const` 可用于声明不希望被修改的值。
- `scanf("%d", &n)` 中 `%d` 要求读整数；`&n` 把变量地址交给函数，让它能写入结果。返回值是成功读到的项目数，因此先检查 `!= 1`。
- `if/else` 按条件选分支；`&&` 是“且”，`||` 是“或”，`!` 是否定。这里 `||` 的右侧可能因为短路而不再执行。
- `for (初始化; 条件; 更新)` 适合已知循环范围；`while (条件)` 适合反复执行直到条件不成立。循环必须考虑终止，否则可能无限运行。
- 数组 `first_five[5]` 有 5 个元素，合法下标是 0～4；`first_five[5]` 越界，不能因为“恰好没崩溃”就认为正确。
- `sum_to(n)` 把“求和”独立成函数。函数的输入是参数，输出是 `return` 的值；每次调用都应能说清参数是什么、返回什么。

## 三、C++ 语法：同样的问题，换一套常用工具

保存为 `02_cpp_basics.cpp`。运行时依次输入 `5` 和 `小明`，各占一行。

```cpp
#include <iostream>
#include <string>
#include <vector>

int sum_to(int n) {
    int sum = 0;
    for (int i = 1; i <= n; ++i) {
        sum += i;
    }
    return sum;
}

int main() {
    int n = 0;
    std::cout << "请输入一个非负整数：";
    if (!(std::cin >> n) || n < 0) {
        std::cerr << "输入无效\n";
        return 1;
    }

    std::string name;
    std::cout << "请输入姓名：";
    std::getline(std::cin >> std::ws, name); // 清掉前面输入留下的空白

    std::vector<int> numbers{1, 2, 3, 4, 5};
    int total = 0;
    for (int value : numbers) {             // 范围 for：逐个取出元素
        total += value;
    }

    std::cout << name << "，1 到 " << n << " 的和是 " << sum_to(n) << '\n';
    std::cout << "容器中的元素个数：" << numbers.size() << '\n';
    std::cout << "容器中的元素之和：" << total << '\n';
    std::cout << (n % 2 == 0 ? "偶数" : "奇数") << '\n';
}
```

输入 `5` 和 `小明` 时，应得到“1 到 5 的和是 15”、元素个数 5、元素之和 15、奇数。若姓名中含空格，`getline` 仍能读取整行；`std::cin >> name` 则通常在空白处停止。这里 `std::ws` 会跳过开头空白，因此**若题目要求保留姓名开头的空格**，就不能直接照搬。

C++ 的 `std::string` 管理字符串长度与存储，`std::vector<int>` 是可动态增减的整数序列；C 的字符数组和固定数组并不会自动拥有这些能力。`std::cout` 是正常输出，`std::cerr` 常用于错误信息。

### 还会经常见到：`while`、`switch`、结构体与引用

`while` 先判断条件再执行，`do ... while` 则至少执行一次；`break` 跳出当前循环或 `switch`，`continue` 跳到本轮循环的下一次判断。`switch` 常用于按整数/枚举值分支；少写 `break` 可能继续执行后面的分支。结构体把几项相关数据组织到一起。

保存为 `07_control_flow.c`，观察为什么结果只统计了三个分数中的合格项：

```c
#include <stdio.h>

struct Student {
    const char *name;
    int score;
};

int main(void) {
    struct Student students[] = {{"A", 90}, {"B", 45}, {"C", 70}};
    int index = 0;
    int passed = 0;
    while (index < 3) {
        if (students[index].score < 60) {
            ++index;
            continue;             // 本次不计入 passed
        }
        ++passed;
        ++index;
    }
    switch (passed) {
        case 0: puts("无人合格"); break;
        case 1: puts("一人合格"); break;
        default: puts("多人合格"); break;
    }
    printf("合格人数：%d\n", passed); // 2
    return 0;
}
```

C++ 中的引用可让函数直接修改调用者的变量；普通值参数只是副本。保存为 `08_reference.cpp`：

```cpp
#include <iostream>

void add_one_copy(int value) { ++value; }
void add_one_reference(int &value) { ++value; }

int main() {
    int score = 5;
    add_one_copy(score);
    std::cout << score << '\n'; // 仍是 5
    add_one_reference(score);
    std::cout << score << '\n'; // 变成 6
}
```

让学生画出调用前后的 `score`，再运行；这比直接背“引用是什么”更容易理解。C 的指针参数也能修改外部变量，但写法不同，见后面的指针与引用小节。

## 四、常用函数先理解“输入—处理—返回”

函数调用形如 `函数名(参数1, 参数2)`。看新函数时先问四件事：**需要哪个头文件？参数是什么类型？返回什么？失败或边界情况怎样处理？** 不要把 `sizeof` 当函数，它是 C/C++ 的运算符。

### C 常用函数速查

| 目的 | 头文件与函数 | 例子与关键点 |
|---|---|---|
|格式化输出 | `<stdio.h>`：`printf`、`puts` | `printf("%d", 3)`；`puts("Hi")` 自动换行 |
|读输入 | `<stdio.h>`：`scanf`、`fgets` | `scanf` 检查返回值；读整行优先用带容量的 `fgets` |
|字符串长度 | `<string.h>`：`strlen` | 不计末尾 `'\0'`；仅适用于正确终止的 C 字符串 |
|比较/查找 | `<string.h>`：`strcmp`、`strchr`、`strstr` | `strcmp(a,b)==0` 才表示内容相等；后两者找不到返回 `NULL` |
|安全格式化 | `<stdio.h>`：`snprintf` | 写入时给出目标数组容量，检查是否截断 |
|字符判断/转换 | `<ctype.h>`：`isdigit`、`tolower` | 判断数字字符、转换大小写；传入 `unsigned char` 值更稳妥 |
|数字转换 | `<stdlib.h>`：`strtol`、`abs` | `strtol` 可检查是否真的读到数字；`abs` 求整数绝对值 |
|数学 | `<math.h>`：`sqrt`、`fabs` | 平方根和浮点绝对值；某些系统链接时要加 `-lm` |

保存下面的完整示例为 `03_c_functions.c`：

```c
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    const char *text = "Hello C";
    printf("长度：%zu\n", strlen(text));             // 7
    printf("比较：%d\n", strcmp("cat", "cat"));     // 0 表示相同

    const char *found = strstr(text, "lo");
    if (found != NULL) {
        printf("子串起点下标：%td\n", found - text); // 3
    }

    char line[32];
    puts("输入一行文字：");
    if (fgets(line, sizeof line, stdin) == NULL) {
        return 1;
    }
    line[strcspn(line, "\n")] = '\0';            // 去掉可能存在的换行
    printf("你输入了：%s\n", line);

    char message[32];
    int written = snprintf(message, sizeof message, "分数=%d", 95);
    if (written < 0 || (size_t)written >= sizeof message) {
        puts("格式化失败或内容被截断");
        return 1;
    }
    puts(message);

    char *end = NULL;
    long number = strtol("42", &end, 10);
    if (end != NULL && *end == '\0') {
        printf("解析结果：%ld\n", number);
    }
    printf("字符：%c，数字字符？%d\n", tolower((unsigned char)'A'),
           isdigit((unsigned char)'7') != 0);
    printf("绝对值：%d，平方根：%.1f\n", abs(-3), sqrt(9.0));
    return 0;
}
```

例如输入 `abc`，可核对长度 7、比较 0、子串下标 3、输入内容 `abc`、`分数=95`、解析结果 42、字符 `a`、数字字符为 1、绝对值 3、平方根 3.0。课堂追问：为什么 `strcmp` 返回 0 才是相等？因为它返回的是比较结果的“差异符号”，不是布尔真值。

### C++ 常用函数/成员函数速查

| 目的 | 头文件与写法 | 例子与关键点 |
|---|---|---|
|输入输出 | `<iostream>`：`std::cin`、`std::cout`；`<string>`：`std::getline` | `std::getline(std::cin, line)` 读一整行 |
|字符串 | `<string>`：`size`、`substr`、`find` | `s.find("ab")` 找不到返回 `std::string::npos` |
|转换 | `<string>`：`std::stoi`、`std::to_string` | `stoi` 对无效输入可抛异常；边界还要考虑越界 |
|容器 | `<vector>`：`push_back`、`size`、`at` | `at` 越界会报错；`operator[]` 不做同样的边界检查 |
|排序/查找 | `<algorithm>`：`sort`、`reverse`、`find`、`max_element` | 算法通常接收 `begin()` 与 `end()` 迭代器 |
|求和 | `<numeric>`：`accumulate` | `std::accumulate(v.begin(), v.end(), 0)` |
|数学 | `<cmath>`：`std::sqrt`、`std::abs` | 整数除法不会因赋值给 double 而自动变成小数除法 |

保存为 `04_cpp_functions.cpp`：

```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

int main() {
    std::string s = "Hello C++";
    std::cout << "长度：" << s.size() << '\n';          // 9
    std::cout << "前三个字符：" << s.substr(0, 3) << '\n';
    auto pos = s.find("C++");
    if (pos != std::string::npos) {
        std::cout << "C++ 起点下标：" << pos << '\n'; // 6
    }

    int number = std::stoi("42");
    std::cout << "转换：" << number << " -> "
              << std::to_string(number) << '\n';

    std::vector<int> values{4, 1, 3};
    values.push_back(2);
    std::sort(values.begin(), values.end());
    std::cout << "排序后：";
    for (int x : values) std::cout << x << ' ';
    std::cout << '\n';                               // 1 2 3 4

    auto it = std::find(values.begin(), values.end(), 3);
    std::cout << "找到 3？" << (it != values.end()) << '\n';
    std::cout << "最大值：" << *std::max_element(values.begin(), values.end()) << '\n';
    std::cout << "总和：" << std::accumulate(values.begin(), values.end(), 0) << '\n';
    std::cout << "平方根：" << std::sqrt(16.0) << '\n';
}
```

这里 `find` 的返回值不是“下标”，而是迭代器；若等于 `values.end()`，就表示未找到。对空容器直接解引用 `max_element` 的结果是不正确的，先判断是否为空。让同学把 `sort` 换成 `reverse`，预测顺序再运行。

## 五、指针与引用：知道它们解决什么问题

C 中函数参数默认传值；在函数内交换两个副本，不会改到外面的变量。若要修改调用者的变量，可以传地址：

```c
// 这段可放在一个已有 #include <stdio.h> 的 C 文件中
void swap_int(int *a, int *b) {
    int temp = *a;   // *a 取地址所指向的值
    *a = *b;
    *b = temp;
}
```

调用时写 `swap_int(&x, &y)`。C++ 可以使用引用参数 `void swap_int(int &a, int &b)`，调用写 `swap_int(x, y)`；引用参数是原变量的别名，不是复制一份。注意 C 和 C++ 的语法不同，不要把 `int &a` 放进 C 文件。初学者先能画出“变量—地址—值”的关系，再继续学动态内存；不要一开始就背复杂的指针声明。

## 六、最容易写错的地方

| 写法/现象 | 问题是什么 | 应怎样想 |
|---|---|---|
|`if (x = 5)` | 把 5 赋给 x，不是在比较 | 比较写 `x == 5`；打开编译警告 |
|`5 / 2` 得到 2 | 两个操作数都是整数 | 想要小数用 `5.0 / 2` 等 |
|数组长度 5 却访问 `a[5]` | 下标从 0 开始，已越界 | 有效下标是 0～4 |
|`scanf("%d", n)` | 没给 `scanf` 写入目标地址 | 写 `&n`，并检查返回值 |
|C 字符串用 `a == b` 比内容 | 比较的是指针/地址 | C 用 `strcmp(a,b)==0`；C++ `std::string` 可用 `==` |
|`std::cin >> n` 后直接 `getline` 得到空行 | 上次输入留下的换行还在 | 了解输入缓冲；按需要处理换行 |
|修改源代码后运行结果没变 | 运行的可能是旧可执行文件 | 重新编译，并确认运行路径 |
|报错“命令找不到” | 可能未安装或 PATH 未命中 | 先找程序，再查 PATH；不是代码语法问题 |

报错时记录：**完整命令、输入、编译器输出、文件路径和版本**。只发一句“代码不对”或仅截最后一行，别人很难复现。

## 七、课堂练习（先做，再看参考实现）

1. 输入一个整数 `n`，输出 1 到 `n` 中所有偶数的和。例：输入 6，输出 12（2+4+6）。先列出 0、1、6 这几个边界输入的预期。
2. 输入三个整数，输出最大值。不得先假设最大值一定为正数；用 `-5 -2 -9` 检验。
3. 对 `std::vector<int>{3,1,3,2}` 排序并统计数字 3 出现次数。说出为什么 `std::sort` 之后仍可遍历计数。
4. 用 C 的 `fgets` 读取一行，输出实际字符数（不计末尾换行）。解释为什么不能直接把 `sizeof 数组` 当作输入长度。

### 练习 1：C 参考实现

保存为 `05_even_sum.c`，输入 6 时输出 12。

```c
#include <stdio.h>

int main(void) {
    int n;
    if (scanf("%d", &n) != 1 || n < 0) {
        puts("输入无效");
        return 1;
    }
    int sum = 0;
    for (int i = 2; i <= n; i += 2) {
        sum += i;
    }
    printf("%d\n", sum);
    return 0;
}
```

### 练习 2：C++ 参考实现

保存为 `06_max3.cpp`，输入 `-5 -2 -9` 时输出 `-2`。

```cpp
#include <algorithm>
#include <iostream>

int main() {
    int a, b, c;
    if (!(std::cin >> a >> b >> c)) return 1;
    std::cout << std::max({a, b, c}) << '\n';
}
```

### 练习 3、4：核对思路

- 排序得到 `1 2 3 3`，计数为 2；`std::count(v.begin(), v.end(), 3)` 是现成算法，也可以自己写循环。排序改变顺序，不改变每个值出现的总次数。
- `fgets` 读取后可用 `strcspn(line, "\n")` 找到换行位置；若缓冲区不够大，可能只读到一部分。需要结合 `strlen` 和是否读到换行判断。`sizeof line` 对固定数组给的是**容量**，不是这次输入的长度。

## 八、课后自查：解释得出才算会

- 我能从 `main` 开始说明代码执行顺序，并预测一个分支/循环的输出吗？
- 我能说出 C 的字符数组与 C++ 的 `std::string` 差异吗？
- 我查一个陌生函数时，会先找头文件、参数、返回值与失败情况吗？
- 我能区分编译错误、运行错误、结果错误，以及“命令找不到”吗？
- 我能把某道题的输入、预期、实际输出和验证过程写给同伴，让对方复现吗？

下一次遇到新函数，不要问“这个函数要不要背”；先用最小程序调用一次、修改参数、观察返回值、查文档核对边界，再决定是否放进自己的速查笔记。
