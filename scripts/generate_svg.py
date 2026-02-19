#!/usr/bin/env python3
"""
SVG 模板生成脚本
将 SVG 模板转为 PNG 源文件（1024x1024）
支持 cairosvg（如可用）或纯 Pillow 回退方案
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# 纯 Pillow 图标绘制（无需 Cairo）
# ============================================================

def draw_rounded_rect(draw, xy, radius, fill):
    """绘制圆角矩形"""
    x0, y0, x1, y1 = xy
    r = radius
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
    draw.pieslice([x0, y0, x0 + 2*r, y0 + 2*r], 180, 270, fill=fill)
    draw.pieslice([x1 - 2*r, y0, x1, y0 + 2*r], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2*r, x0 + 2*r, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2*r, y1 - 2*r, x1, y1], 0, 90, fill=fill)


def make_gradient(size, color1, color2):
    """创建渐变背景"""
    img = Image.new("RGBA", (size, size))
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size)
            r = int(color1[0] * (1 - t) + color2[0] * t)
            g = int(color1[1] * (1 - t) + color2[1] * t)
            b = int(color1[2] * (1 - t) + color2[2] * t)
            img.putpixel((x, y), (r, g, b, 255))
    return img


def create_main_icon(size=1024):
    """创建主图标 - 渐变背景 + 钻石图案"""
    # 渐变背景
    img = make_gradient(size, (102, 126, 234), (118, 75, 162))
    draw = ImageDraw.Draw(img)

    # 圆角蒙版
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    margin = int(size * 0.0625)
    radius = int(size * 0.176)
    draw_rounded_rect(mask_draw, (margin, margin, size - margin, size - margin), radius, 255)
    
    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg.paste(img, mask=mask)
    img = bg
    draw = ImageDraw.Draw(img)

    # 钻石图形
    cx, cy = size // 2, int(size * 0.47)
    s = size * 0.27  # 缩放系数
    
    # 上部梯形
    top_pts = [
        (cx - s*0.71, cy - s*0.43),
        (cx + s*0.71, cy - s*0.43),
        (cx + s, cy - s*0.07),
        (cx - s, cy - s*0.07),
    ]
    draw.polygon(top_pts, fill=(255, 255, 255, 240))
    
    # 下部三角
    bottom_pts = [
        (cx - s, cy - s*0.07),
        (cx + s, cy - s*0.07),
        (cx, cy + s),
    ]
    draw.polygon(bottom_pts, fill=(255, 255, 255, 215))
    
    # 切面线
    left_pts = [
        (cx - s, cy - s*0.07),
        (cx - s*0.29, cy - s*0.07),
        (cx, cy + s),
    ]
    draw.polygon(left_pts, fill=(232, 232, 255, 128))

    right_pts = [
        (cx + s*0.29, cy - s*0.07),
        (cx + s, cy - s*0.07),
        (cx, cy + s),
    ]
    draw.polygon(right_pts, fill=(216, 216, 255, 128))

    # ICON 文字
    try:
        font = ImageFont.truetype("arial.ttf", int(size * 0.094))
    except (OSError, IOError):
        font = ImageFont.load_default()
    
    text = "ICON"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    tx = (size - tw) // 2
    ty = int(size * 0.82)
    draw.text((tx, ty), text, fill=(255, 255, 255, 230), font=font)

    return img


def create_app_icon(size=1024):
    """创建应用图标 - 绿色渐变 + 闪电"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 圆形背景
    cx, cy = size // 2, size // 2
    r = int(size * 0.45)
    
    # 渐变圆
    for y_off in range(-r, r + 1):
        for x_off in range(-r, r + 1):
            if x_off**2 + y_off**2 <= r**2:
                t = (x_off + y_off + 2*r) / (4*r)
                cr = int(67 * (1 - t) + 56 * t)
                cg = int(233 * (1 - t) + 249 * t)
                cb = int(123 * (1 - t) + 215 * t)
                img.putpixel((cx + x_off, cy + y_off), (cr, cg, cb, 255))

    # 闪电
    s = size * 0.27
    pts = [
        (cx - s*0.15, cy - s),
        (cx + s*0.22, cy - s*0.14),
        (cx - s*0.07, cy - s*0.14),
        (cx + s*0.15, cy + s),
        (cx - s*0.22, cy + s*0.14),
        (cx + s*0.07, cy + s*0.14),
    ]
    draw.polygon(pts, fill=(255, 255, 255, 245))

    return img


def create_web_icon(size=1024):
    """创建 Web 图标 - 粉黄渐变 + 地球"""
    img = make_gradient(size, (250, 112, 154), (254, 225, 64))
    draw = ImageDraw.Draw(img)

    # 圆角蒙版
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    margin = int(size * 0.0625)
    radius = int(size * 0.125)
    draw_rounded_rect(mask_draw, (margin, margin, size - margin, size - margin), radius, 255)
    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg.paste(img, mask=mask)
    img = bg
    draw = ImageDraw.Draw(img)

    # 地球
    cx, cy = size // 2, size // 2
    r = int(size * 0.254)
    lw = max(int(size * 0.035), 2)
    
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline=(255,255,255,255), width=lw)
    # 椭圆经线
    draw.ellipse((cx-r//2, cy-r, cx+r//2, cy+r), outline=(255,255,255,255), width=lw)
    # 水平赤道
    draw.line((cx-r, cy, cx+r, cy), fill=(255,255,255,255), width=lw)
    # 纬线
    draw.arc((cx-r, cy-r*0.7, cx+r, cy-r*0.15), 0, 180, fill=(255,255,255,200), width=lw)
    draw.arc((cx-r, cy+r*0.15, cx+r, cy+r*0.7), 0, 180, fill=(255,255,255,200), width=lw)

    return img


def create_logo_icon(size=1024):
    """创建 Logo 图标 - 蓝色渐变 + L 字母"""
    img = make_gradient(size, (79, 172, 254), (0, 242, 254))
    draw = ImageDraw.Draw(img)

    # 圆角蒙版
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    margin = int(size * 0.0625)
    radius = int(size * 0.195)
    draw_rounded_rect(mask_draw, (margin, margin, size - margin, size - margin), radius, 255)
    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg.paste(img, mask=mask)
    img = bg
    draw = ImageDraw.Draw(img)

    # L 字母
    cx, cy = size // 2, int(size * 0.488)
    bar_w = int(size * 0.078)
    bar_r = int(size * 0.02)
    
    # 竖线
    vx = cx - int(size * 0.195)
    vy = cy - int(size * 0.254)
    vh = int(size * 0.508)
    draw_rounded_rect(draw, (vx, vy, vx + bar_w, vy + vh), bar_r, (255,255,255,255))
    
    # 横线
    hy = vy + vh - bar_w
    hw = int(size * 0.39)
    draw_rounded_rect(draw, (vx, hy, vx + hw, hy + bar_w), bar_r, (255,255,255,255))
    
    # 装饰圆点
    dot_r = int(size * 0.049)
    dot_cx = vx + hw + int(size * 0.039)
    dot_cy = hy + bar_w // 2
    draw.ellipse((dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r), 
                 fill=(255, 255, 255, 200))

    return img


# ============================================================
# SVG → PNG (使用 cairosvg，如果可用)
# ============================================================

def try_cairosvg(svg_path, png_path, size=1024):
    """尝试使用 cairosvg 转换"""
    try:
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=png_path,
                         output_width=size, output_height=size)
        return True
    except (ImportError, OSError):
        return False


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(project_root, "src")
    os.makedirs(src_dir, exist_ok=True)

    print("🎨 图标 PNG 生成")
    print("=" * 40)

    # 尝试 cairosvg
    main_svg = os.path.join(src_dir, "icon.svg")
    use_cairo = False
    if os.path.exists(main_svg):
        test_path = os.path.join(src_dir, "_test.png")
        use_cairo = try_cairosvg(main_svg, test_path)
        if os.path.exists(test_path):
            os.remove(test_path)

    if use_cairo:
        print("  使用 cairosvg 引擎")
        import cairosvg
        # 转换主图标
        png_path = os.path.join(src_dir, "icon.png")
        cairosvg.svg2png(url=main_svg, write_to=png_path, output_width=1024, output_height=1024)
        print(f"  ✅ icon.svg → icon.png (1024x1024)")

        # 转换模板
        templates_dir = os.path.join(project_root, "templates")
        if os.path.exists(templates_dir):
            for svg_file in os.listdir(templates_dir):
                if svg_file.endswith(".svg"):
                    svg_path = os.path.join(templates_dir, svg_file)
                    png_name = svg_file.replace(".svg", ".png")
                    png_path = os.path.join(src_dir, png_name)
                    cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=1024, output_height=1024)
                    print(f"  ✅ {svg_file} → {png_name} (1024x1024)")
    else:
        print("  cairosvg 不可用，使用 Pillow 绘制引擎")
        
        # 主图标
        icon = create_main_icon(1024)
        icon.save(os.path.join(src_dir, "icon.png"), "PNG")
        print(f"  ✅ icon.png (1024x1024)")

        # 模板图标
        templates = {
            "app-icon.png": create_app_icon,
            "web-icon.png": create_web_icon,
            "logo-icon.png": create_logo_icon,
        }
        for name, creator in templates.items():
            img = creator(1024)
            img.save(os.path.join(src_dir, name), "PNG")
            print(f"  ✅ {name} (1024x1024)")

    print()
    print("✅ 所有图标 PNG 已生成")
    print(f"📁 输出目录: {src_dir}")


if __name__ == "__main__":
    main()
