# 📦 CopyParty Desktop 打包指南

## 🎯 概述

CopyParty Desktop v2.0 提供了完整的多平台打包解决方案，支持 Windows、macOS 和 Linux 平台的可执行文件生成和分发包创建。

## 🛠️ 环境准备

### 基础要求
- Python 3.8+
- PyQt6 >= 6.5.0
- PyInstaller >= 5.0

### 安装依赖
```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装打包工具
pip install pyinstaller

# 安装开发依赖 (可选)
pip install -e ".[dev]"
```

### 平台特定要求

#### Windows
- **NSIS** (可选): 用于创建安装包
- **Visual Studio Build Tools**: 编译某些依赖

#### macOS
- **Xcode Command Line Tools**: 基础开发工具
- **create-dmg** (可选): 创建DMG镜像

#### Linux
- **build-essential**: 基础编译工具
- **python3-dev**: Python开发头文件

## 🚀 快速打包

### 方法1: 快速打包脚本 (推荐用于测试)
```bash
# 一键快速打包
python quick_build.py
```

这个脚本会：
- ✅ 检查依赖
- 🔨 使用PyInstaller单文件模式打包
- 🧪 简单测试生成的可执行文件
- 📦 输出到 `dist/` 目录

### 方法2: 完整构建流程 (推荐用于发布)
```bash
# 完整构建 (包含测试和安装包)
python build.py

# 跳过测试
python build.py --skip-tests

# 跳过安装包创建
python build.py --skip-installer

# 仅清理
python build.py --clean-only
```

## 🔧 详细构建流程

### 1. 生成PyInstaller配置
```bash
python build_spec.py
```

这会生成平台特定的 `.spec` 文件，包含：
- 数据文件收集
- 隐藏导入配置
- 平台特定设置
- 图标和资源

### 2. 手动PyInstaller构建
```bash
# 使用生成的.spec文件
pyinstaller copyparty_desktop_windows_amd64.spec

# 或直接使用命令行
pyinstaller --onefile --windowed main.py
```

### 3. 创建分发包

#### Windows
```bash
# 使用NSIS创建安装包 (需要安装NSIS)
makensis installer.nsi
```

#### macOS
```bash
# 创建DMG镜像
hdiutil create -volname "CopyParty Desktop" -srcfolder dist/CopyPartyDesktop.app -ov -format UDZO CopyPartyDesktop.dmg
```

#### Linux
```bash
# 创建tar.gz包
tar -czf CopyPartyDesktop-linux-x64.tar.gz -C dist/ CopyPartyDesktop
```

## 📁 输出文件结构

### Windows
```
dist/
├── CopyPartyDesktop.exe          # 主可执行文件
├── CopyPartyDesktop-Setup.exe    # 安装包 (可选)
└── ...
```

### macOS
```
dist/
├── CopyPartyDesktop.app/         # 应用包
├── CopyPartyDesktop.dmg          # DMG镜像 (可选)
└── ...
```

### Linux
```
dist/
├── CopyPartyDesktop              # 可执行文件
├── CopyPartyDesktop-linux-x64.tar.gz  # 分发包 (可选)
└── ...
```

## 🧪 测试构建结果

### 自动测试
构建脚本会自动运行以下测试：
- 配置系统测试
- UI组件测试
- 协议扩展测试
- 高优先级功能测试

### 手动测试
```bash
# 测试可执行文件
./dist/CopyPartyDesktop --version

# 测试GUI启动
./dist/CopyPartyDesktop

# 测试配置加载
./dist/CopyPartyDesktop --config test_config.yaml
```

## 🔍 故障排除

### 常见问题

#### 1. 导入错误
```
ModuleNotFoundError: No module named 'xxx'
```
**解决方案**: 在 `.spec` 文件中添加到 `hiddenimports` 列表

#### 2. 资源文件缺失
```
FileNotFoundError: [Errno 2] No such file or directory: 'xxx'
```
**解决方案**: 在 `.spec` 文件中添加到 `datas` 列表

#### 3. PyQt6相关错误
```
qt.qpa.plugin: Could not load the Qt platform plugin
```
**解决方案**: 确保PyQt6完整安装，添加Qt插件路径

#### 4. 文件过大
**解决方案**: 
- 使用 `--exclude-module` 排除不需要的模块
- 启用UPX压缩 (如果可用)
- 考虑使用目录模式而非单文件模式

### 调试技巧

#### 启用详细输出
```bash
pyinstaller --log-level DEBUG your_spec.spec
```

#### 检查依赖
```bash
# 分析导入依赖
pyi-archive_viewer dist/CopyPartyDesktop.exe

# 检查缺失模块
python -c "import sys; print(sys.path)"
```

#### 测试导入
```python
# 测试所有关键模块导入
import core.application
import protocols.base_protocol
import features.file_indexing
print("所有模块导入成功")
```

## 📊 构建优化

### 减小文件大小
1. **排除不需要的模块**:
   ```python
   excludes = ['tkinter', 'matplotlib', 'numpy', 'scipy']
   ```

2. **使用UPX压缩**:
   ```python
   upx=True,
   upx_exclude=[],
   ```

3. **优化导入**:
   - 只导入需要的子模块
   - 使用延迟导入

### 提高启动速度
1. **减少隐藏导入**
2. **优化初始化代码**
3. **使用目录模式** (而非单文件)

### 提高兼容性
1. **测试多个Python版本**
2. **在虚拟机中测试**
3. **使用CI/CD自动化测试**

## 🔄 持续集成

### GitHub Actions 示例
```yaml
name: Build CopyParty Desktop

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build application
      run: python build.py --skip-installer
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: CopyPartyDesktop-${{ matrix.os }}
        path: dist/
```

## 📋 发布检查清单

### 构建前
- [ ] 更新版本号 (`VERSION` 文件)
- [ ] 更新变更日志 (`CHANGELOG.md`)
- [ ] 运行所有测试
- [ ] 检查依赖版本
- [ ] 清理临时文件

### 构建后
- [ ] 测试所有平台的可执行文件
- [ ] 验证文件大小合理
- [ ] 检查启动时间
- [ ] 测试核心功能
- [ ] 验证配置加载

### 发布前
- [ ] 创建发布说明
- [ ] 准备安装指南
- [ ] 更新文档
- [ ] 标记Git版本
- [ ] 上传到发布平台

## 🎯 最佳实践

1. **版本控制**: 使用语义化版本号
2. **自动化**: 使用CI/CD自动化构建
3. **测试**: 在多个环境中测试
4. **文档**: 保持构建文档更新
5. **备份**: 保留构建配置和脚本

---

## 📞 支持

如果在打包过程中遇到问题：

1. 查看 [故障排除](#-故障排除) 部分
2. 检查 [GitHub Issues](https://github.com/copyparty/copyparty-desktop/issues)
3. 提交新的Issue并附上详细的错误信息

**构建愉快！** 🚀
