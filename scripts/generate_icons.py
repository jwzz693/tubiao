#!/usr/bin/env python3
"""
图标资源生成主脚本
从 1024x1024 PNG 源文件生成所有平台所需的图标格式

支持:
- Windows ICO (多尺寸嵌入)
- macOS ICNS (通过 PNG 组合)
- Favicon (ICO + PNG)
- Apple Touch Icons
- Android Icons (各 DPI)
- PWA Icons
- 通用 PNG 多尺寸
- Electron 应用图标
- 社交媒体预览图
"""

import json
import os
import shutil
import struct
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("❌ 缺少 Pillow 库，请运行: pip install Pillow")
    sys.exit(1)


# ============================================================
# 配置
# ============================================================

# 各平台所需尺寸
ICON_SIZES = {
    "windows": [16, 24, 32, 48, 64, 128, 256],
    "favicon": [16, 32, 48],
    "apple_touch": [120, 152, 167, 180],
    "android": {
        "ldpi": 36,
        "mdpi": 48,
        "hdpi": 72,
        "xhdpi": 96,
        "xxhdpi": 144,
        "xxxhdpi": 192,
    },
    "pwa": [72, 96, 128, 144, 152, 192, 384, 512],
    "png_standard": [16, 24, 32, 48, 64, 96, 128, 256, 512, 1024],
    "electron": {
        "windows": [16, 24, 32, 48, 64, 128, 256],
        "macos": [16, 32, 64, 128, 256, 512, 1024],
        "linux": [16, 24, 32, 48, 64, 128, 256, 512],
    },
    "social": {
        "og_image": (1200, 630),       # Open Graph
        "twitter_card": (1200, 600),    # Twitter Card
        "youtube_thumb": (1280, 720),   # YouTube 缩略图
    }
}


def load_config(project_root):
    """加载配置"""
    config_path = os.path.join(project_root, "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def ensure_dir(path):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def resize_icon(source_img, size, keep_aspect=True):
    """
    高质量缩放图标
    """
    if isinstance(size, tuple):
        target_w, target_h = size
    else:
        target_w = target_h = size

    if keep_aspect and target_w == target_h:
        img = source_img.copy()
        img.thumbnail((target_w, target_h), Image.LANCZOS)
        # 居中放置
        if img.size != (target_w, target_h):
            canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
            offset_x = (target_w - img.width) // 2
            offset_y = (target_h - img.height) // 2
            canvas.paste(img, (offset_x, offset_y))
            return canvas
        return img
    else:
        return source_img.resize((target_w, target_h), Image.LANCZOS)


# ============================================================
# Windows ICO 生成
# ============================================================

def generate_windows_ico(source_img, output_dir):
    """生成 Windows ICO 文件（包含多尺寸）"""
    print("\n🪟  Windows ICO")
    ensure_dir(output_dir)

    sizes = ICON_SIZES["windows"]
    icon_images = []

    for size in sizes:
        img = resize_icon(source_img, size)
        icon_images.append(img)
        # 也保存单独的 PNG
        img.save(os.path.join(output_dir, f"icon-{size}x{size}.png"), "PNG")
        print(f"  ✅ icon-{size}x{size}.png")

    # 保存 ICO（多尺寸合并）
    ico_path = os.path.join(output_dir, "icon.ico")
    icon_images[0].save(
        ico_path,
        format="ICO",
        sizes=[(s, s) for s in sizes if s <= 256],
        append_images=icon_images[1:]
    )
    print(f"  ✅ icon.ico (含 {len([s for s in sizes if s <= 256])} 个尺寸)")


# ============================================================
# macOS ICNS 生成（通过 PNG 集合）
# ============================================================

def generate_macos_icons(source_img, output_dir):
    """生成 macOS 图标集"""
    print("\n🍎 macOS Icons")
    ensure_dir(output_dir)

    macos_sizes = {
        "icon_16x16": 16,
        "icon_16x16@2x": 32,
        "icon_32x32": 32,
        "icon_32x32@2x": 64,
        "icon_128x128": 128,
        "icon_128x128@2x": 256,
        "icon_256x256": 256,
        "icon_256x256@2x": 512,
        "icon_512x512": 512,
        "icon_512x512@2x": 1024,
    }

    iconset_dir = os.path.join(output_dir, "AppIcon.iconset")
    ensure_dir(iconset_dir)

    for name, size in macos_sizes.items():
        img = resize_icon(source_img, size)
        img.save(os.path.join(iconset_dir, f"{name}.png"), "PNG")
        print(f"  ✅ {name}.png ({size}x{size})")

    print(f"  📁 AppIcon.iconset/ 已创建")
    print(f"  💡 在 macOS 上运行: iconutil -c icns AppIcon.iconset")


# ============================================================
# Favicon 生成
# ============================================================

def generate_favicon(source_img, output_dir):
    """生成网站 Favicon"""
    print("\n🌐 Favicon")
    ensure_dir(output_dir)

    sizes = ICON_SIZES["favicon"]

    for size in sizes:
        img = resize_icon(source_img, size)
        img.save(os.path.join(output_dir, f"favicon-{size}x{size}.png"), "PNG")
        print(f"  ✅ favicon-{size}x{size}.png")

    # ICO 格式的 favicon
    images_for_ico = [resize_icon(source_img, s) for s in sizes]
    ico_path = os.path.join(output_dir, "favicon.ico")
    images_for_ico[0].save(
        ico_path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=images_for_ico[1:]
    )
    print(f"  ✅ favicon.ico")

    # 生成 HTML 引用代码
    html_snippet = """<!-- Favicon 引用代码 -->
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
"""
    with open(os.path.join(output_dir, "favicon-usage.html"), "w", encoding="utf-8") as f:
        f.write(html_snippet)
    print(f"  📄 favicon-usage.html（引用代码）")


# ============================================================
# Apple Touch Icons
# ============================================================

def generate_apple_touch(source_img, output_dir):
    """生成 Apple Touch Icons"""
    print("\n📱 Apple Touch Icons")
    ensure_dir(output_dir)

    sizes = ICON_SIZES["apple_touch"]

    for size in sizes:
        img = resize_icon(source_img, size)
        img.save(os.path.join(output_dir, f"apple-touch-icon-{size}x{size}.png"), "PNG")
        print(f"  ✅ apple-touch-icon-{size}x{size}.png")

    # 默认尺寸 180x180
    img_180 = resize_icon(source_img, 180)
    img_180.save(os.path.join(output_dir, "apple-touch-icon.png"), "PNG")
    print(f"  ✅ apple-touch-icon.png (默认 180x180)")

    # HTML snippet
    html_snippet = """<!-- Apple Touch Icon 引用代码 -->
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="apple-touch-icon" sizes="120x120" href="/apple-touch-icon-120x120.png">
<link rel="apple-touch-icon" sizes="152x152" href="/apple-touch-icon-152x152.png">
<link rel="apple-touch-icon" sizes="167x167" href="/apple-touch-icon-167x167.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon-180x180.png">
"""
    with open(os.path.join(output_dir, "apple-touch-usage.html"), "w", encoding="utf-8") as f:
        f.write(html_snippet)
    print(f"  📄 apple-touch-usage.html（引用代码）")


# ============================================================
# Android Icons
# ============================================================

def generate_android(source_img, output_dir):
    """生成 Android 各 DPI 图标"""
    print("\n🤖 Android Icons")
    ensure_dir(output_dir)

    for dpi, size in ICON_SIZES["android"].items():
        dpi_dir = os.path.join(output_dir, f"mipmap-{dpi}")
        ensure_dir(dpi_dir)
        img = resize_icon(source_img, size)
        img.save(os.path.join(dpi_dir, "ic_launcher.png"), "PNG")
        print(f"  ✅ mipmap-{dpi}/ic_launcher.png ({size}x{size})")

    # 圆形图标（Android 自适应图标）
    for dpi, size in ICON_SIZES["android"].items():
        dpi_dir = os.path.join(output_dir, f"mipmap-{dpi}")
        img = resize_icon(source_img, size)
        # 创建圆形蒙版
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size - 1, size - 1), fill=255)
        img_round = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        img_round.paste(img, mask=mask)
        img_round.save(os.path.join(dpi_dir, "ic_launcher_round.png"), "PNG")
        print(f"  ✅ mipmap-{dpi}/ic_launcher_round.png ({size}x{size})")


# ============================================================
# PWA Icons
# ============================================================

def generate_pwa(source_img, output_dir, config):
    """生成 PWA 图标"""
    print("\n📦 PWA Icons")
    ensure_dir(output_dir)

    sizes = ICON_SIZES["pwa"]
    icons_manifest = []

    for size in sizes:
        img = resize_icon(source_img, size)
        filename = f"icon-{size}x{size}.png"
        img.save(os.path.join(output_dir, filename), "PNG")
        icons_manifest.append({
            "src": f"/icons/{filename}",
            "sizes": f"{size}x{size}",
            "type": "image/png",
            "purpose": "any maskable"
        })
        print(f"  ✅ {filename}")

    # 生成 manifest.json
    app_name = config.get("app_name", "MyApp")
    theme_color = config.get("theme_color", "#4a90d9")
    bg_color = config.get("background_color", "#ffffff")

    manifest = {
        "name": app_name,
        "short_name": app_name,
        "start_url": "/",
        "display": "standalone",
        "background_color": bg_color,
        "theme_color": theme_color,
        "icons": icons_manifest
    }

    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"  📄 manifest.json")


# ============================================================
# 通用 PNG 各尺寸
# ============================================================

def generate_png_sizes(source_img, output_dir):
    """生成通用 PNG 多尺寸图标"""
    print("\n🖼️  PNG 多尺寸")
    ensure_dir(output_dir)

    sizes = ICON_SIZES["png_standard"]

    for size in sizes:
        img = resize_icon(source_img, size)
        img.save(os.path.join(output_dir, f"icon-{size}x{size}.png"), "PNG")
        print(f"  ✅ icon-{size}x{size}.png")


# ============================================================
# SVG 复制
# ============================================================

def generate_svg(project_root, output_dir):
    """复制 SVG 源文件到输出目录"""
    print("\n✏️  SVG 矢量图标")
    ensure_dir(output_dir)

    src_svg = os.path.join(project_root, "src", "icon.svg")
    if os.path.exists(src_svg):
        shutil.copy2(src_svg, os.path.join(output_dir, "icon.svg"))
        print(f"  ✅ icon.svg")
    else:
        print(f"  ⚠️  未找到 src/icon.svg")

    # 复制模板
    templates_dir = os.path.join(project_root, "templates")
    if os.path.exists(templates_dir):
        for f in os.listdir(templates_dir):
            if f.endswith(".svg"):
                shutil.copy2(
                    os.path.join(templates_dir, f),
                    os.path.join(output_dir, f)
                )
                print(f"  ✅ {f}")


# ============================================================
# Electron 图标
# ============================================================

def generate_electron(source_img, output_dir):
    """生成 Electron 应用图标"""
    print("\n⚡ Electron Icons")
    ensure_dir(output_dir)

    # Windows
    win_dir = os.path.join(output_dir, "win")
    ensure_dir(win_dir)
    win_sizes = ICON_SIZES["electron"]["windows"]
    win_images = [resize_icon(source_img, s) for s in win_sizes]
    ico_path = os.path.join(win_dir, "icon.ico")
    win_images[0].save(
        ico_path, format="ICO",
        sizes=[(s, s) for s in win_sizes if s <= 256],
        append_images=win_images[1:]
    )
    print(f"  ✅ win/icon.ico")

    # macOS - 保存 1024x1024 PNG（electron-builder 会自动转 icns）
    mac_dir = os.path.join(output_dir, "mac")
    ensure_dir(mac_dir)
    img_1024 = resize_icon(source_img, 1024)
    img_1024.save(os.path.join(mac_dir, "icon.png"), "PNG")
    print(f"  ✅ mac/icon.png (1024x1024)")

    # Linux
    linux_dir = os.path.join(output_dir, "linux")
    ensure_dir(linux_dir)
    for size in ICON_SIZES["electron"]["linux"]:
        img = resize_icon(source_img, size)
        img.save(os.path.join(linux_dir, f"icon-{size}x{size}.png"), "PNG")
    # 默认图标
    img_512 = resize_icon(source_img, 512)
    img_512.save(os.path.join(linux_dir, "icon.png"), "PNG")
    print(f"  ✅ linux/ ({len(ICON_SIZES['electron']['linux'])} 个尺寸)")


# ============================================================
# 社交媒体图标
# ============================================================

def generate_social(source_img, output_dir, config):
    """生成社交媒体预览图"""
    print("\n📢 社交媒体图标")
    ensure_dir(output_dir)

    bg_color = config.get("background_color", "#ffffff")
    # 解析颜色
    if bg_color.startswith("#"):
        r = int(bg_color[1:3], 16)
        g = int(bg_color[3:5], 16)
        b = int(bg_color[5:7], 16)
    else:
        r, g, b = 255, 255, 255

    for name, (width, height) in ICON_SIZES["social"].items():
        canvas = Image.new("RGBA", (width, height), (r, g, b, 255))

        # 将图标居中放置
        icon_size = min(width, height) - 100
        icon = resize_icon(source_img, icon_size)

        offset_x = (width - icon.width) // 2
        offset_y = (height - icon.height) // 2
        canvas.paste(icon, (offset_x, offset_y), icon)

        canvas.save(os.path.join(output_dir, f"{name}.png"), "PNG")
        print(f"  ✅ {name}.png ({width}x{height})")


# ============================================================
# 主流程
# ============================================================

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config = load_config(project_root)

    # 查找源图标
    source_path = os.path.join(project_root, config.get("source", "src/icon.png"))

    if not os.path.exists(source_path):
        # 尝试 SVG → PNG
        svg_path = os.path.join(project_root, "src", "icon.svg")
        if os.path.exists(svg_path):
            print("📌 未找到 PNG 源文件，尝试从 SVG 生成...")
            try:
                import cairosvg
                cairosvg.svg2png(url=svg_path, write_to=source_path,
                                output_width=1024, output_height=1024)
                print(f"  ✅ SVG → PNG 转换完成")
            except ImportError:
                print("❌ 需要 cairosvg 来转换 SVG")
                print("请运行: pip install cairosvg")
                print("或手动提供 1024x1024 的 PNG 文件到 src/icon.png")
                sys.exit(1)
        else:
            print(f"❌ 未找到源图标文件: {source_path}")
            print("请将 1024x1024 PNG 放到 src/icon.png")
            sys.exit(1)

    print("🎨 图标资源生成工具")
    print("=" * 50)
    print(f"📁 源文件: {source_path}")

    # 加载源图标
    source_img = Image.open(source_path).convert("RGBA")
    print(f"📐 源尺寸: {source_img.size[0]}x{source_img.size[1]}")

    if source_img.size[0] < 512 or source_img.size[1] < 512:
        print("⚠️  建议使用至少 1024x1024 的源图标以获得最佳质量")

    dist_dir = os.path.join(project_root, "dist")
    formats = config.get("formats", {})

    # 清空并重建输出目录
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)

    # === 生成各类图标 ===

    if formats.get("windows_ico", True):
        generate_windows_ico(source_img, os.path.join(dist_dir, "windows"))

    if formats.get("macos_icns", True):
        generate_macos_icons(source_img, os.path.join(dist_dir, "macos"))

    if formats.get("favicon", True):
        generate_favicon(source_img, os.path.join(dist_dir, "favicon"))

    if formats.get("apple_touch", True):
        generate_apple_touch(source_img, os.path.join(dist_dir, "apple-touch"))

    if formats.get("android", True):
        generate_android(source_img, os.path.join(dist_dir, "android"))

    if formats.get("pwa", True):
        generate_pwa(source_img, os.path.join(dist_dir, "pwa"), config)

    if formats.get("png_sizes", True):
        generate_png_sizes(source_img, os.path.join(dist_dir, "png"))

    if formats.get("svg", True):
        generate_svg(project_root, os.path.join(dist_dir, "svg"))

    if formats.get("electron", True):
        generate_electron(source_img, os.path.join(dist_dir, "electron"))

    if formats.get("social", True):
        generate_social(source_img, os.path.join(dist_dir, "social"), config)

    # 总结
    print()
    print("=" * 50)
    print("🎉 所有图标生成完成!")
    print(f"📁 输出目录: {dist_dir}")

    # 统计文件数
    total_files = 0
    for root, dirs, files in os.walk(dist_dir):
        total_files += len(files)
    print(f"📊 共生成 {total_files} 个文件")
    print()
    print("💡 提示: 用浏览器打开 preview.html 预览所有图标")


if __name__ == "__main__":
    main()
