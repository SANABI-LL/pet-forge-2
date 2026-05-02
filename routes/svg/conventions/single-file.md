# 自包含单文件范式

> SVG 路线的工程承诺：**一个 `.svg.html` = 完整可运行桌宠动画**。零外部依赖、零构建步骤、双击即跑。

---

## 范式定义

每个状态文件长这样：

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>状态名</title>
  <style>
    /* 内联 CSS，不引外部 .css */
  </style>
</head>
<body>
  <svg viewBox="...">
    <!-- 内联 SVG -->
  </svg>
  <script>
    /* 内联 JS，不引外部 .js */
  </script>
</body>
</html>
```

**没有**：
- ❌ `<link rel="stylesheet">` 引外部 CSS
- ❌ `<script src="...">` 引外部 JS
- ❌ `import` / `require` / npm 依赖
- ❌ 构建步骤（webpack / vite / parcel）
- ❌ Server / 后端

**有**：
- ✅ 内联 `<style>`
- ✅ 内联 `<script>`
- ✅ 内联 SVG（不是 `<img src="x.svg">`）

---

## 为什么这么严格

1. **双击即跑**：用户拿到一个文件，浏览器打开就看到动画。零部署成本。
2. **改一改，刷一刷**：改完保存，浏览器刷新就生效。无构建反馈循环。
3. **可分享**：发给朋友 = 发一个文件。不用 zip、不用建仓库。
4. **运行时友好**：Electron / Tauri / WebView 等桌宠 runtime 加载单文件最简单。
5. **AI 友好**：AI 助手一次性看完整个状态，比跨多文件追代码快得多。
6. **诊断简单**：动画不对劲，打开文件看 DOM + console，不需要 source map。

---

## 文件命名约定

### 状态文件

格式：**`<状态名>-<方向>-v<N>.svg.html`**

```
idle-eye-follow-v1.svg.html       ← idle 状态、眼睛跟随方向、第 1 版
idle-breathing-v1.svg.html        ← idle 状态、呼吸方向、第 1 版（不同方向，平起平坐）
idle-eye-follow-v2.svg.html       ← v1 之后的方向迭代
typing-stroke-symbols-v4.svg.html ← typing 状态、描边代码符号方向、第 4 版
```

**v1 / v2 / v3 是方向迭代，不是修补丁**：
- v2 不是 "v1 的 bugfix"，是 "v1 试了之后发现方向不对，换了个新方向"
- 同一方向小修小补，直接覆盖原文件
- 真要保存修补节点，用 `-tuned` / `-final` / `-backup-before-merge` 后缀

### 锁定/归档

```
confirmed/states/<state>-<approach>-vN.svg.html   ← 当前推荐版本（链接）
_archive/<state>-跑偏方向.svg.html                ← 已废弃但保留追溯
_locked-backups/<state>-vN-backup-2026-MM-DD.svg.html  ← 锁定前的版本备份
```

**跑偏方向不删**，归档进 `_archive/`。理由：
- 后续磨制可能想"绕回去看看那条路是不是真的死胡同"
- 跑偏的具体原因是元教训源头，删了就丢了

---

## 跨状态共用资产怎么办（看似违反单文件原则）

桌宠多状态会有共用资产：眼形库、嘴形库、纸飞机、帽子、眼罩...

**做法**：每个状态文件**内联复制**共用资产，**不**通过 `<use href="...">` 跨文件引用。

理由：
- `<use href="external.svg">` 破坏自包含
- 复制成本低（几十行代码），收益大（仍然双击即跑）
- 共用资产真改了，搜替换批量改，不影响范式

但**库文件**（`library/`）保留作为**源头参考**：
- `library/eye-shapes.svg` 是源头，维护者和 AI 助手改这里
- 状态文件从 library 复制粘贴最新版本进去
- 库文件本身也是 svg.html 形式，可以单独打开看

---

## 启动模板

`routes/svg/templates/hello-idle.svg.html` 是**最小起点**：

- 一个圆球角色 + 呼吸 + 眨眼
- 套 apple-precise preset 默认值
- 带详细注释解释每个 CSS 变量
- ~150 行整个文件

用户复制一份重命名成自己的状态名，改 `<g id="pet">` 内的造型，就开始了。

---

## 反面：什么情况下 break 范式

只有一个情况：**多个角色共用一份动画引擎**（比如同一个 idle 给 5 个角色用，引擎相同造型不同）。

这时可以：
- 共用引擎抽到 `engine.js` 单独维护
- 每个角色文件还是 svg.html，但 `<script>` 用 `import` 拉引擎

**但 pet-forge 第一版不支持这个**。一上来就走标准单文件，不要为"未来可能"留口子。
