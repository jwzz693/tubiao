#!/usr/bin/env python3
"""
PWA manifest.json 生成脚本
"""
import json
import os
import sys


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    config_path = os.path.join(project_root, "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {}

    app_name = config.get("app_name", "MyApp")
    theme_color = config.get("theme_color", "#4a90d9")
    bg_color = config.get("background_color", "#ffffff")

    pwa_sizes = [72, 96, 128, 144, 152, 192, 384, 512]

    icons = []
    for size in pwa_sizes:
        icons.append({
            "src": f"icons/icon-{size}x{size}.png",
            "sizes": f"{size}x{size}",
            "type": "image/png",
            "purpose": "any maskable"
        })

    manifest = {
        "name": app_name,
        "short_name": app_name,
        "description": f"{app_name} - Progressive Web App",
        "start_url": "/",
        "display": "standalone",
        "orientation": "portrait",
        "background_color": bg_color,
        "theme_color": theme_color,
        "icons": icons
    }

    output_path = os.path.join(project_root, "dist", "pwa", "manifest.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"✅ manifest.json 已生成: {output_path}")

    # 同时生成 browserconfig.xml (Windows 磁贴)
    browserconfig = """<?xml version="1.0" encoding="utf-8"?>
<browserconfig>
  <msapplication>
    <tile>
      <square70x70logo src="/icons/icon-72x72.png"/>
      <square150x150logo src="/icons/icon-144x144.png"/>
      <square310x310logo src="/icons/icon-384x384.png"/>
      <TileColor>{theme_color}</TileColor>
    </tile>
  </msapplication>
</browserconfig>""".format(theme_color=theme_color)

    bc_path = os.path.join(project_root, "dist", "pwa", "browserconfig.xml")
    with open(bc_path, "w", encoding="utf-8") as f:
        f.write(browserconfig)
    print(f"✅ browserconfig.xml 已生成: {bc_path}")


if __name__ == "__main__":
    main()
