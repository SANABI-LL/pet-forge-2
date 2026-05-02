# png2svg —— 扁平桌宠/吉祥物专用 PNG 矢量化流水线

> 来源：pet-forge 的公开 PNG-to-SVG 辅助工具。
> 用途：把 1 张 PNG（去过背景的扁平角色）转成 SVG，准备进 SVG 路线动画工作流。
> 适用：扁平卡通、低色块、像素风、纯色 + 圆角凸起类角色。

---

## ⚠️ 环境陷阱（必读）

**vtracer 0.6.15 在 Python 3.14 上会段错误。必须用 Python 3.13。**

Windows 推荐：
```powershell
py -3.13 png2svg.py <input.png>
```

如果你只有 3.14，先装 3.13：
```powershell
# 方法 1: pyenv-win 或 Microsoft Store 装 3.13
# 方法 2: 官网下载 https://www.python.org/downloads/release/python-3130/
```

---

## 安装依赖

```powershell
py -3.13 -m pip install Pillow numpy scipy vtracer
```

依赖说明：
- **Pillow** —— 图像加载/缩放/量化
- **numpy** —— 像素操作
- **scipy** —— 去背景的 flood fill 标注
- **vtracer** —— 核心矢量化（Rust 写的 Python binding）

### 核心矢量化引擎：vtracer

本工具不自己手写 tracer。真正的 PNG/JPG → SVG 路径追踪由 [`vtracer`](https://github.com/visioncortex/vtracer) 完成；`png2svg.py` 只做桌宠工作流需要的前后处理：

- 清理透明像素底下的脏 RGB，避免透明区域生成大量无意义 path
- 用 flood fill 兜底移除纯色背景
- 先把颜色量化成少量色块，减少路径数量
- 小图放大后再追踪，避免低分辨率锯齿直接进 SVG
- 用 `presets.json` 固化桌宠常用参数

vtracer 的原理不是简单描边。它会先做颜色/像素聚类，再对聚类区域做 path walking、路径简化、角点保留平滑和曲线拟合。对这类通用矢量化算法，直接用成熟引擎比在本仓库里手搓可靠得多。

**限制必须说清楚：SVG 路线只推荐简单图形。** 适合干净边界、低色数、扁平卡通、像素风、logo/图标类素材；不适合照片、复杂插画、毛发、透明半影、强渐变、噪点和纹理很多的图。复杂图形会出现 path 爆炸、文件巨大、边缘变脏、颜色分层怪、细节丢失等问题。这类素材优先走 APNG 路线，或手工重画关键 SVG 结构。

### 推荐去背景工具：rembg

如果输入 PNG 不是透明背景，推荐先用 [`rembg`](https://github.com/danielgatis/rembg) 生成透明背景版本，再交给 `png2svg.py`。

```powershell
py -3.13 -m pip install "rembg[cpu,cli]"
py -3.13 -m rembg i input.png input-clean.png
```

说明：
- `rembg` 是外部可选工具，不是 pet-forge 内置依赖。
- 官方要求 Python `>=3.11,<3.14`，所以和本工具推荐的 Python 3.13 对齐。
- 第一次运行会下载模型到本机缓存目录；离线环境需要提前准备模型。

---

## 用法

### 基本用法

```powershell
py -3.13 png2svg.py input-clean.png output.svg --preset apple-precise
```

如果不写输出路径，默认输出同名 `.svg`。

### 查看预设

```powershell
py -3.13 png2svg.py --list-presets
```

### 指定 preset / 颜色数 / 放大倍数

```powershell
py -3.13 png2svg.py input-clean.png output.svg --preset pixel-art --n-colors 16 --scale 1
```

推荐参数：
- `--preset`：读取 `presets.json`，默认 `apple-precise`
- `--n-colors`：覆盖 preset 的量化色数，建议 4-32
- `--scale`：覆盖 preset 的放大倍数，可填 `auto` 或正整数

兼容旧位置参数：

```powershell
py -3.13 png2svg.py input.png output.svg 16 4
```

---

## 5 步流水线说明

```
[1/5] 加载 + 清理透明像素   ← 防 vtracer path 爆炸
[2/5] 去背景                 ← scipy flood fill 从四角检测
[3/5] 色彩量化               ← PIL median cut，渐变压成纯色块
[4/5] 放大                   ← LANCZOS，小图自动 4x，大图不放
[5/5] vtracer 矢量化         ← 位图 → SVG path
```

---

## 风格预调参（preset）

`presets.json` 里有针对不同风格的参数预设。建议直接用对应 preset，避免手调 vtracer 的 10 个黑盒参数。

```powershell
py -3.13 png2svg.py input-clean.png output.svg --preset apple-precise
py -3.13 png2svg.py input-clean.png output.svg --preset pixel-art
py -3.13 png2svg.py --list-presets
```

### apple-precise（扁平卡通 / 圆角凸起）

```json
{
  "n_colors": 8,
  "scale": "auto",
  "vtracer": {
    "filter_speckle": 48,
    "color_precision": 6,
    "layer_difference": 32,
    "corner_threshold": 80,
    "length_threshold": 8.0,
    "splice_threshold": 45,
    "path_precision": 2,
    "mode": "spline"
  }
}
```

适用：圆润、低色块、有机形状角色（云朵 / 软糖 / 圆角字符）。

### pixel-art

```json
{
  "n_colors": 16,
  "scale": 1,
  "vtracer": {
    "filter_speckle": 0,
    "color_precision": 8,
    "layer_difference": 0,
    "corner_threshold": 180,
    "length_threshold": 1.0,
    "splice_threshold": 0,
    "path_precision": 0,
    "mode": "polygon"
  }
}
```

适用：整像素角色（FC / GBA 风）。`mode: polygon` 保留直角。

---

## 6 个痛点（已知问题）

| # | 痛点 | 状态 | 解决思路 |
|---|---|---|---|
| 1 | 必须 py 3.13 | 文档已标 | 等 vtracer 修 3.14 段错误 |
| 2 | vtracer 10 参数全是黑盒 | 已缓解 | `--preset` + presets.json |
| 3 | CLI 一次性，没交互 | 待解决 | 加 `--watch` 模式 |
| 4 | 没预览/对比 | 待解决 | 加输出 HTML 含原图 + SVG 对比 |
| 5 | 没"小尺寸 preview 先确认" | 待解决 | 加 `--preview` 跑缩略图先 |
| 6 | 通用矢量化非桌宠专用 | 部分缓解 | presets.json 针对桌宠预调，复杂图仍建议 APNG |

当前已解决环境说明和参数预设；预览、交互和更强的复杂图判定留后续迭代。

---

## 如何用在 SVG 路线工作流

```
1. 用户去 AI 网页生 / 自己画 / Figma 导一张 PNG
2. 如果不是透明背景 → 先用 rembg 去背景：
   py -3.13 -m pip install "rembg[cpu,cli]"
   py -3.13 -m rembg i input.png input-clean.png
3. py -3.13 png2svg.py input-clean.png character.svg --preset apple-precise
4. 把 character.svg 的 path 复制到 routes/svg/templates/hello-idle.svg.html 的 <g id="pet"> 里
5. 调 hello-idle 的 CSS 变量适配自己的角色
6. 在浏览器双击打开看动画
```

---

## 调参经验

实际跑出来不满意时按这个顺序调：

1. **path 太多/太碎** → 加 `filter_speckle`（48 → 80）
2. **颜色丢失** → 加 `n_colors`（8 → 16）
3. **角太尖** → 减 `corner_threshold`（80 → 60）
4. **角太圆** → 加 `corner_threshold`（80 → 120）
5. **整体形状抓不准** → 减 `path_precision`（2 → 1）
6. **路径锯齿严重** → 加 `path_precision`（2 → 4）

---

## 来源 + 版本

- 本仓库版本：公开整理版，已接入 presets.json。
- 核心矢量化引擎：vtracer，MIT 开源项目，见 https://github.com/visioncortex/vtracer 。
- 许可边界：pet-forge 自写 README/包装说明按 MIT；如后续从其他项目继续搬入代码，需要保留对应来源和许可说明。
