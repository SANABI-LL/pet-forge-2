#!/usr/bin/env python3
"""PNG → SVG 矢量化流水线 (预处理 → 量化 → vtracer 矢量化)

注意: vtracer 0.6.15 在 Python 3.14 上会段错误，需用 py -3.13 运行。
"""
import argparse
import json
import os
import sys
from pathlib import Path


DEFAULT_PRESET_NAME = 'apple-precise'
DEFAULT_VTRACER_PARAMS = {
    'colormode': 'color',
    'hierarchical': 'stacked',
    'mode': 'spline',
    'filter_speckle': 48,
    'color_precision': 6,
    'layer_difference': 32,
    'corner_threshold': 80,
    'length_threshold': 8.0,
    'max_iterations': 10,
    'splice_threshold': 45,
    'path_precision': 2,
}
DEFAULT_PRESETS = {
    DEFAULT_PRESET_NAME: {
        '_description': '扁平卡通 / 圆角凸起 / 软橡胶质感角色',
        'n_colors': 8,
        'scale': 'auto',
        'vtracer': DEFAULT_VTRACER_PARAMS,
    }
}


def load_presets():
    """读取同目录 presets.json；缺失时回退到内置默认预设。"""
    preset_path = Path(__file__).with_name('presets.json')
    if not preset_path.exists():
        return DEFAULT_PRESETS

    with preset_path.open('r', encoding='utf-8') as f:
        raw = json.load(f)

    presets = {
        name: value
        for name, value in raw.items()
        if isinstance(value, dict) and isinstance(value.get('vtracer'), dict)
    }
    return presets or DEFAULT_PRESETS


def print_presets(presets):
    print("可用 presets:")
    for name, preset in presets.items():
        desc = preset.get('_description', '')
        n_colors = preset.get('n_colors', 8)
        scale = preset.get('scale', 'auto')
        print(f"  {name:<14} n_colors={n_colors:<3} scale={scale}  {desc}")


def parse_cli(argv):
    parser = argparse.ArgumentParser(
        description='PNG -> SVG 矢量化流水线；核心矢量化由 vtracer 完成。'
    )
    parser.add_argument('input', nargs='?', help='输入 PNG 文件')
    parser.add_argument('output', nargs='?', help='输出 SVG 路径，默认同名 .svg')
    parser.add_argument(
        'legacy_n_colors',
        nargs='?',
        type=int,
        help='兼容旧用法的位置参数：量化色数',
    )
    parser.add_argument(
        'legacy_scale',
        nargs='?',
        help='兼容旧用法的位置参数：放大倍数或 auto',
    )
    parser.add_argument(
        '--preset',
        default=DEFAULT_PRESET_NAME,
        help=f'读取 presets.json 中的预设，默认 {DEFAULT_PRESET_NAME}',
    )
    parser.add_argument(
        '--n-colors',
        type=int,
        help='覆盖 preset 的量化色数，建议 4-32',
    )
    parser.add_argument(
        '--scale',
        help='覆盖 preset 的放大倍数；可填 auto 或正整数',
    )
    parser.add_argument(
        '--list-presets',
        action='store_true',
        help='列出可用预设后退出',
    )
    return parser.parse_args(argv)


def normalize_scale(value):
    text = str(value).strip().lower()
    if text == 'auto':
        return 'auto'
    scale = int(text)
    if scale < 1:
        raise ValueError('scale 必须是 auto 或正整数')
    return scale


def resolve_settings(args, presets):
    if args.preset not in presets:
        available = ', '.join(presets)
        raise ValueError(f"未知 preset: {args.preset}。可用: {available}")

    preset = presets[args.preset]
    n_colors = (
        args.n_colors
        if args.n_colors is not None
        else args.legacy_n_colors
        if args.legacy_n_colors is not None
        else int(preset.get('n_colors', 8))
    )
    if not 4 <= n_colors <= 64:
        raise ValueError('n_colors 建议在 4-64 之间')

    scale_value = (
        args.scale
        if args.scale is not None
        else args.legacy_scale
        if args.legacy_scale is not None
        else preset.get('scale', 'auto')
    )
    scale = normalize_scale(scale_value)

    vtracer_params = DEFAULT_VTRACER_PARAMS.copy()
    vtracer_params.update(preset.get('vtracer', {}))
    return n_colors, scale, vtracer_params


def load_and_prepare(input_path):
    """加载图片，统一透明像素 RGB（防止 vtracer path 爆炸）"""
    from PIL import Image
    import numpy as np

    img = Image.open(input_path).convert('RGBA')
    arr = np.array(img)
    print(f"  原始: {img.width}x{img.height}")

    # 透明/半透明像素的 RGB 统一为白色
    # 不做这一步，vtracer 会把透明区域底下的杂色 RGB 当独立颜色，导致 path 爆炸
    mask = arr[:, :, 3] < 128
    arr[mask, :3] = 255
    arr[mask, 3] = 0

    transparent_pct = mask.sum() * 100 // (arr.shape[0] * arr.shape[1])
    print(f"  透明像素: {transparent_pct}%")

    return Image.fromarray(arr)


def remove_background(img, tolerance=60):
    """scipy flood fill 从四角检测背景 → 设为透明（已透明的图片可跳过）"""
    import numpy as np
    from scipy.ndimage import label

    arr = np.array(img)
    h, w = arr.shape[:2]

    # 检查是否已有大量透明像素
    transparent_pct = (arr[:, :, 3] < 128).sum() * 100 // (h * w)
    if transparent_pct > 10:
        print(f"  已有 {transparent_pct}% 透明像素，跳过去背景")
        return img

    # 四角采样背景色
    corners = [arr[0, 0, :3], arr[0, w-1, :3], arr[h-1, 0, :3], arr[h-1, w-1, :3]]
    bg_color = np.median(corners, axis=0).astype(np.uint8)
    print(f"  检测背景色: rgb({bg_color[0]},{bg_color[1]},{bg_color[2]})")

    diff = np.abs(arr[:, :, :3].astype(int) - bg_color.astype(int)).sum(axis=2)
    bg_mask = diff < tolerance

    labeled, num_features = label(bg_mask)
    corner_labels = set()
    for y, x in [(0, 0), (0, w-1), (h-1, 0), (h-1, w-1)]:
        if labeled[y, x] > 0:
            corner_labels.add(labeled[y, x])

    removed = 0
    for lbl in corner_labels:
        m = labeled == lbl
        removed += m.sum()
        arr[m, 3] = 0

    print(f"  移除背景: {removed} px ({removed * 100 // (h * w)}%)")

    from PIL import Image as PILImage
    return PILImage.fromarray(arr)


def quantize_colors(img, n_colors=8):
    """色彩量化，把渐变压成纯色块"""
    from PIL import Image as PILImage
    import numpy as np

    arr = np.array(img)
    alpha = arr[:, :, 3].copy()

    rgb = PILImage.fromarray(arr[:, :, :3])
    quantized = rgb.quantize(colors=n_colors, method=PILImage.Quantize.MEDIANCUT).convert('RGB')

    result = np.dstack([np.array(quantized), alpha])
    print(f"  量化为 {n_colors} 色")
    return PILImage.fromarray(result)


def upscale(img, scale):
    """Pillow LANCZOS 放大（大图可跳过）"""
    from PIL import Image
    if scale <= 1:
        print(f"  跳过放大 (scale={scale})")
        return img
    new_size = (img.width * scale, img.height * scale)
    print(f"  放大 {scale}x: {img.width}x{img.height} → {new_size[0]}x{new_size[1]}")
    return img.resize(new_size, Image.LANCZOS)


def vectorize(img, output_path, **overrides):
    """vtracer 位图→矢量SVG"""
    import vtracer
    import io

    params = DEFAULT_VTRACER_PARAMS.copy()
    params.update(overrides)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_bytes = buf.getvalue()

    svg_str = vtracer.convert_raw_image_to_svg(
        img_bytes=img_bytes,
        img_format='png',
        **params
    )

    Path(output_path).write_text(svg_str, encoding='utf-8')
    path_count = svg_str.count('<path')
    print(f"  生成 {path_count} 条 path, {len(svg_str) // 1024}KB")
    return svg_str


def auto_scale(img):
    """根据图片大小自动决定放大倍数"""
    pixels = img.width * img.height
    if pixels >= 1_000_000:  # >= 1MP, 不放大
        return 1
    elif pixels >= 250_000:  # >= 0.25MP, 2x
        return 2
    else:  # 小图, 4x
        return 4


def main():
    args = parse_cli(sys.argv[1:])
    presets = load_presets()

    if args.list_presets:
        print_presets(presets)
        return

    if not args.input:
        print("用法: py -3.13 png2svg.py <input.png> [output.svg] [n_colors] [scale]")
        print("推荐: py -3.13 png2svg.py input-clean.png output.svg --preset apple-precise")
        print("预设: py -3.13 png2svg.py --list-presets")
        print("注意: vtracer 在 Python 3.14 上段错误，请用 py -3.13 运行")
        sys.exit(1)

    input_path = args.input
    if not os.path.exists(input_path):
        print(f"错误: 文件不存在 {input_path}")
        sys.exit(1)

    stem = Path(input_path).stem
    output_path = args.output if args.output else f"{stem}.svg"

    try:
        n_colors, scale_setting, vtracer_params = resolve_settings(args, presets)
    except ValueError as exc:
        print(f"错误: {exc}")
        sys.exit(1)

    print(f"preset: {args.preset}")

    print("[1/5] 加载 + 清理透明像素 ...")
    img = load_and_prepare(input_path)

    print("[2/5] 去背景 ...")
    img = remove_background(img)

    print("[3/5] 色彩量化 ...")
    img = quantize_colors(img, n_colors)

    scale = auto_scale(img) if scale_setting == 'auto' else scale_setting
    print(f"[4/5] 放大 (scale={scale}) ...")
    img = upscale(img, scale)

    print("[5/5] vtracer 矢量化 ...")
    vectorize(img, output_path, **vtracer_params)

    print(f"Done -> {output_path}")


if __name__ == '__main__':
    main()
