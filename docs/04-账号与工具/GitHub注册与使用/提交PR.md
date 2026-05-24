# 如何提交 Pull Request（PR）

PR（Pull Request）是 GitHub 上协作的核心方式——你把自己的修改提交给别人的仓库，仓库所有者审核后决定是否合并。无论是给开源项目贡献代码、修复文档错误，还是给本手册提交内容，都走这个流程。

---

## 整体流程

```
Fork 仓库 → 修改内容 → 提交 PR → 等待合并
```

---

## 第一步：Fork 仓库

打开目标仓库页面，点击右上角的 **Fork** 按钮：

![Fork 按钮位于仓库页面右上角](https://docs.github.com/assets/cb-40742/mw-1440/images/help/repository/fork-button.webp)

Fork 会在你自己的账号下创建一份完整的仓库副本，你对这个副本拥有完整权限，可以随意修改。

---

## 第二步：修改内容

### 方式一：在网页上直接编辑（适合小改动）

1. 进入你 Fork 后的仓库（地址形如 `github.com/你的用户名/仓库名`）
2. 找到要修改的文件，点击右上角铅笔图标 **Edit this file**
3. 直接在网页编辑器里修改
4. 修改完成后，在页面下方 **Commit changes** 填写说明后提交

### 方式二：克隆到本地编辑（适合大改动）

```bash
# 1. 克隆你 Fork 的仓库到本地
git clone https://github.com/你的用户名/仓库名.git
cd 仓库名

# 2. 创建新分支（不要直接在 main 上改）
git checkout -b fix/my-changes

# 3. 修改文件...

# 4. 提交
git add .
git commit -m "描述你的修改内容"

# 5. 推送到你的 Fork
git push origin fix/my-changes
```

---

## 第三步：创建 Pull Request

修改提交后，GitHub 会在你的仓库页面顶部出现提示横幅：

> **Compare & pull request**

点击这个按钮，或者手动进入 **Pull requests → New pull request**。

填写 PR 信息：

| 字段 | 填写建议 |
|---|---|
| **标题** | 简洁描述做了什么，例如「修复 CLion 配置图片路径」 |
| **描述** | 说明改动原因、内容，有截图更好 |
| **base**（目标） | 选原仓库的 `main` 分支 |
| **compare**（来源） | 选你 Fork 后的分支 |

确认无误后点击 **Create pull request**。

---

## 第四步：等待审核

PR 提交后，仓库维护者会收到通知，审核你的改动：

- **直接合并**：改动被接受，恭喜
- **要求修改**：维护者留下 Review 评论，按要求修改后重新 push 到同一分支，PR 会自动更新
- **关闭**：改动不适合合并（会说明原因）

---

## 给本手册提 PR

本手册仓库地址：[github.com/starnotes-xj/SurviveBIGCManual](https://github.com/starnotes-xj/SurviveBIGCManual)

文档文件全部在 `docs/` 目录下，Markdown 格式，直接在网页编辑器里改就行，不需要本地搭建环境。详细规范见 [贡献指南](../../贡献指南.md)。

!!! tip "第一次提 PR 不要怕"
    PR 不会直接生效，维护者审核后才会合并。改错了也没关系，只会影响你自己的 Fork，不会破坏原仓库。
