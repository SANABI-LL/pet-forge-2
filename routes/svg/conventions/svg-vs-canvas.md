# 工具选择宪法：SVG vs Canvas

> 本宪法只对 **pet-forge SVG 路线**生效。APNG 路线 AI 直接生帧，不存在"用什么技术实现"的选择。

---

## 一句话规则

> **默认 SVG。SVG 撞墙才上 Canvas。撞墙的判断只有一条：是否需要"真 3D 曲面 / 网格变形 / 大量独立粒子"。**

---

## SVG 优势（默认选它的原因）

1. **声明式动画**：CSS animation / SMIL 一行写完循环，零运行时开销
2. **DOM 可检视**：浏览器 DevTools 直接看每个元素，调参像改 CSS 一样直接
3. **无限缩放**：矢量数据，不糊
4. **文件小**：一个 idle 状态通常 < 50KB
5. **零依赖运行**：浏览器原生支持，不引任何库
6. **热改友好**：用户改一个数值立刻看效果，不用重新编译/重打包

## Canvas 撞墙的真实场景（罕见）

- **真 3D 曲面**：球面 / 椭球面投影，需要逐像素深度计算 → SVG 做不到
- **网格变形**：羽毛飘动、布料动力学、流体扭曲 → SVG path 数学上做得到但性能爆炸
- **大量独立粒子**：50+ 颗粒子各自独立物理运动 → SVG DOM 节点性能墙

> 桌宠绝大多数动画都达不到这个门槛。多数二维桌宠状态用 SVG 就足够。

---

## 硬性禁止

不允许：

- ❌ **同一动画文件 SVG 和 canvas 混用**：增加心智负担、丢失声明式优势
- ❌ **基础动作（idle / 眨眼）用 canvas**：杀鸡用牛刀、调试痛苦
- ❌ **canvas 文件依赖外部库**：违反"自包含单文件"范式（详见 `single-file.md`）

---

## 误判 Canvas 的常见情况

新手常误判"这个用 SVG 做不到，要 Canvas"，但其实 SVG 能做，只是没想到：

| 看似要 Canvas | 其实 SVG 能做 |
|---|---|
| 粒子效果 | `<circle>` × N + CSS animation 各自不同 delay |
| 鼠标跟随眼睛 | `<g>` + JS transform 跟踪 mousemove |
| 形变（圆 → 方） | path d 属性插值 + `<animate>` 或 GSAP morphSVG |
| 弹性弹跳 | cubic-bezier 缓动 + transform scale/translate |
| 心形粒子飘 | 多个 path × CSS animation × random delay |
| 笔触效果 | `stroke-dasharray` + `stroke-dashoffset` 动画 |

**先问"SVG 真的不能吗"再考虑 Canvas**。多数情况下答案是 SVG 能做。

---

## 反面教训

> 曾经有 idle 状态因为过早选 Canvas 跑偏。真正的问题不是 SVG 做不到，而是开工前没有先看参考和重读约束。

教训：**做新动画前两件必做**：
1. 看类似已有作品（`reference/` 或现有 confirmed 状态）
2. 重读本宪法 + `single-file.md`

---

## 何时 Canvas 真的合适

如果你确认要做：

- 流体模拟（水、烟、火）
- 复杂粒子系统（500+ 粒子带物理）
- 真 3D 渲染（不是 fake 3D 错觉）
- 大量像素级图像处理（实时滤镜）

**且这些是动画必需而非装饰** —— 那 Canvas。否则 SVG。

---

## 写在最后

这条宪法看起来限制大，但实际上**99% 的桌宠动画 SVG 都能做**，宪法只是把"避免误用 Canvas"的判断成本降到零。
