#!/usr/bin/env python3
"""
PyInstaller 打包配置生成器
为不同平台生成对应的.spec文件
"""

import os
import sys
import platform

def get_platform_info():
    """获取平台信息"""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == 'windows':
        return 'windows', arch, '.exe'
    elif system == 'darwin':
        return 'macos', arch, '.app'
    elif system == 'linux':
        return 'linux', arch, ''
    else:
        return system, arch, ''

def generate_spec_content():
    """生成.spec文件内容"""
    system, arch, ext = get_platform_info()
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
"""
CopyParty Desktop PyInstaller 配置
平台: {system}-{arch}
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(SPEC))
sys.path.insert(0, project_root)

# 收集数据文件
datas = []

# 添加资源文件
if os.path.exists(os.path.join(project_root, 'resources')):
    datas.extend(collect_data_files('resources'))

# 添加UI主题文件
ui_themes_path = os.path.join(project_root, 'ui', 'themes')
if os.path.exists(ui_themes_path):
    for file in os.listdir(ui_themes_path):
        if file.endswith(('.qss', '.css')):
            datas.append((os.path.join(ui_themes_path, file), 'ui/themes'))

# 添加配置文件
config_files = [
    'COPYPARTY_COMPLETENESS_ANALYSIS.md',
    'README.md',
    'CHANGELOG.md'
]

for config_file in config_files:
    config_path = os.path.join(project_root, config_file)
    if os.path.exists(config_path):
        datas.append((config_path, '.'))

# 收集隐藏导入
hiddenimports = [
    # PyQt6 模块
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtNetwork',
    
    # 项目模块
    'core.application',
    'core.config_manager',
    'core.server_manager',
    'core.plugin_manager',
    
    # 配置模块
    'config.base_config',
    'config.server_config',
    'config.network_config',
    'config.security_config',
    'config.upload_config',
    
    # 协议模块
    'protocols.base_protocol',
    'protocols.http_server',
    'protocols.ftp_server',
    'protocols.webdav_server',
    'protocols.smb_server',
    
    # UI模块
    'ui.main_window',
    'ui.widgets.server_control',
    'ui.widgets.config_editor',
    'ui.widgets.monitoring_panel',
    'ui.widgets.protocol_config',
    'ui.widgets.file_index_widget',
    
    # 功能模块
    'features.file_indexing',
    'security.authentication',
    
    # 第三方模块
    'sqlite3',
    'hashlib',
    'secrets',
    'threading',
    'multiprocessing',
    'psutil',
    'yaml',
    'toml'
]

# 排除的模块
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'jupyter',
    'IPython'
]

# 分析配置
a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 处理重复文件
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 可执行文件配置
exe_name = 'CopyPartyDesktop{ext}'
'''

    # 平台特定配置
    if system == 'windows':
        spec_content += '''
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windows GUI应用
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/app.ico'  # Windows图标
)
'''
    elif system == 'macos':
        spec_content += '''
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CopyPartyDesktop',
)

app = BUNDLE(
    coll,
    name='CopyParty Desktop.app',
    icon='resources/icons/app.icns',  # macOS图标
    bundle_identifier='com.copyparty.desktop',
    info_plist={{
        'CFBundleName': 'CopyParty Desktop',
        'CFBundleDisplayName': 'CopyParty Desktop',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False
    }}
)
'''
    else:  # Linux
        spec_content += '''
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    return spec_content

def create_spec_file():
    """创建.spec文件"""
    system, arch, ext = get_platform_info()
    spec_filename = f'copyparty_desktop_{system}_{arch}.spec'
    
    spec_content = generate_spec_content()
    
    with open(spec_filename, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✓ 已生成 {spec_filename}")
    return spec_filename

if __name__ == "__main__":
    spec_file = create_spec_file()
    print(f"使用以下命令进行打包:")
    print(f"pyinstaller {spec_file}")
