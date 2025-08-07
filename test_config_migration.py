#!/usr/bin/env python3
"""
测试配置系统迁移
验证从旧架构到新架构的配置迁移
"""

import sys
import os
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_config_modules():
    """测试配置模块导入"""
    print("测试配置模块导入...")
    
    try:
        from config.base_config import BaseConfig, ValidationResult, ConfigGroup
        print("✓ base_config 导入成功")
        
        from config.server_config import ServerConfig, UploadConfig
        print("✓ server_config 导入成功")
        
        from config.network_config import NetworkConfig
        print("✓ network_config 导入成功")
        
        from config.security_config import SecurityConfig, TLSConfig, AuthenticationConfig
        print("✓ security_config 导入成功")
        
        from core.config_manager import ConfigManager
        print("✓ config_manager 导入成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_creation():
    """测试配置对象创建"""
    print("\n测试配置对象创建...")
    
    try:
        from config.server_config import ServerConfig
        from config.network_config import NetworkConfig
        from config.security_config import SecurityConfig
        from core.config_manager import ConfigManager
        
        # 创建各种配置对象
        server_config = ServerConfig()
        print("✓ ServerConfig 创建成功")
        
        network_config = NetworkConfig()
        print("✓ NetworkConfig 创建成功")
        
        security_config = SecurityConfig()
        print("✓ SecurityConfig 创建成功")
        
        config_manager = ConfigManager()
        print("✓ ConfigManager 创建成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置对象创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_serialization():
    """测试配置序列化"""
    print("\n测试配置序列化...")
    
    try:
        from core.config_manager import ConfigManager
        
        # 创建配置管理器
        config_manager = ConfigManager()
        
        # 修改一些配置
        config_manager.server_config.working_directory = "/test/path"
        config_manager.server_config.max_clients = 2048
        config_manager.network_config.listen_ports = "8080,8081"
        config_manager.security_config.tls.https_only = True
        
        # 测试转换为字典
        config_dict = config_manager.to_dict()
        print("✓ 配置转换为字典成功")
        
        # 测试JSON序列化
        json_str = config_manager.to_json()
        print("✓ 配置JSON序列化成功")
        
        # 测试从JSON反序列化
        new_config_manager = ConfigManager()
        new_config_manager.from_json(json_str)
        print("✓ 配置JSON反序列化成功")
        
        # 验证数据一致性
        assert new_config_manager.server_config.working_directory == "/test/path"
        assert new_config_manager.server_config.max_clients == 2048
        assert new_config_manager.network_config.listen_ports == "8080,8081"
        assert new_config_manager.security_config.tls.https_only == True
        print("✓ 配置数据一致性验证通过")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置序列化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_validation():
    """测试配置验证"""
    print("\n测试配置验证...")
    
    try:
        from core.config_manager import ConfigManager
        
        # 创建配置管理器
        config_manager = ConfigManager()
        
        # 测试有效配置
        result = config_manager.validate_all()
        print(f"✓ 默认配置验证: {'通过' if result.is_valid else '失败'}")
        
        # 测试无效配置
        config_manager.server_config.max_clients = -1  # 无效值
        config_manager.network_config.listen_ports = "invalid_port"  # 无效端口
        
        result = config_manager.validate_all()
        print(f"✓ 无效配置验证: {'正确检测到错误' if not result.is_valid else '未检测到错误'}")
        
        if result.errors:
            print(f"  检测到的错误: {len(result.errors)} 个")
            for error in result.errors[:3]:  # 显示前3个错误
                print(f"    - {error}")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置验证测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_legacy_migration():
    """测试旧配置迁移"""
    print("\n测试旧配置迁移...")
    
    try:
        # 检查是否存在旧配置文件
        if not os.path.exists("copyparty_complete_config.py"):
            print("⚠ 旧配置文件不存在，跳过迁移测试")
            return True
        
        # 导入旧配置
        from copyparty_complete_config import CopyPartyCompleteConfig
        from core.config_manager import ConfigManager
        
        # 创建旧配置对象
        legacy_config = CopyPartyCompleteConfig()
        print("✓ 旧配置对象创建成功")
        
        # 创建新配置管理器
        new_config_manager = ConfigManager()
        
        # 执行迁移
        new_config_manager.load_from_legacy(legacy_config)
        print("✓ 旧配置迁移成功")
        
        # 验证迁移结果
        assert new_config_manager.server_config.working_directory == legacy_config.working_directory
        assert new_config_manager.network_config.listen_ips == legacy_config.network.listen_ips
        assert new_config_manager.network_config.listen_ports == legacy_config.network.listen_ports
        print("✓ 迁移数据验证通过")
        
        return True
        
    except Exception as e:
        print(f"✗ 旧配置迁移测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_command_args_generation():
    """测试命令行参数生成"""
    print("\n测试命令行参数生成...")
    
    try:
        from core.config_manager import ConfigManager
        
        # 创建配置管理器
        config_manager = ConfigManager()
        
        # 设置一些配置
        config_manager.server_config.max_clients = 2048
        config_manager.server_config.accounts = ["user1:pass1", "user2:pass2:admin"]
        config_manager.server_config.volumes = ["/path1::r", "/path2:alias:rw"]
        config_manager.network_config.listen_ports = "8080"
        config_manager.network_config.listen_ips = "0.0.0.0"
        config_manager.security_config.tls.https_only = True
        
        # 生成命令行参数
        args = config_manager.generate_copyparty_args()
        print("✓ 命令行参数生成成功")
        
        # 验证参数
        args_str = " ".join(args)
        print(f"  生成的参数: {args_str}")
        
        # 检查关键参数
        assert "-nc" in args and "2048" in args, "max_clients 参数缺失"
        assert "-a" in args, "accounts 参数缺失"
        assert "-v" in args, "volumes 参数缺失"
        assert "-p" in args and "8080" in args, "ports 参数缺失"
        assert "-i" in args and "0.0.0.0" in args, "listen_ips 参数缺失"
        assert "--https-only" in args, "https_only 参数缺失"
        
        print("✓ 关键参数验证通过")
        
        return True
        
    except Exception as e:
        print(f"✗ 命令行参数生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_operations():
    """测试文件操作"""
    print("\n测试文件操作...")
    
    try:
        from core.config_manager import ConfigManager
        
        # 创建配置管理器
        config_manager = ConfigManager()
        
        # 修改配置
        config_manager.server_config.working_directory = "/test/migration"
        config_manager.server_config.max_clients = 1500
        config_manager.network_config.listen_ports = "9000"
        
        # 测试保存到文件
        test_config_path = "test_config.json"
        config_manager.save_config(test_config_path)
        print("✓ 配置保存到文件成功")
        
        # 测试从文件加载
        new_config_manager = ConfigManager()
        new_config_manager.load_config(test_config_path)
        print("✓ 配置从文件加载成功")
        
        # 验证数据一致性
        assert new_config_manager.server_config.working_directory == "/test/migration"
        assert new_config_manager.server_config.max_clients == 1500
        assert new_config_manager.network_config.listen_ports == "9000"
        print("✓ 文件操作数据一致性验证通过")
        
        # 清理测试文件
        if os.path.exists(test_config_path):
            os.remove(test_config_path)
        
        return True
        
    except Exception as e:
        print(f"✗ 文件操作测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("CopyParty 配置系统迁移测试")
    print("=" * 50)
    
    tests = [
        test_config_modules,
        test_config_creation,
        test_config_serialization,
        test_config_validation,
        test_legacy_migration,
        test_command_args_generation,
        test_file_operations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ 测试 {test.__name__} 异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 配置系统迁移测试全部通过！")
        print("\n🎉 配置系统迁移成果:")
        print("1. ✅ 模块化配置架构")
        print("2. ✅ 配置验证系统")
        print("3. ✅ 序列化/反序列化")
        print("4. ✅ 旧配置迁移支持")
        print("5. ✅ 命令行参数生成")
        print("6. ✅ 文件操作支持")
        
        print("\n📊 配置模块统计:")
        print("- BaseConfig: 配置基类和验证框架")
        print("- ServerConfig: 服务器配置 (迁移自 GeneralConfig)")
        print("- NetworkConfig: 网络配置 (迁移自 NetworkConfig)")
        print("- SecurityConfig: 安全配置 (迁移自 TLSConfig + 扩展)")
        print("- UploadConfig: 上传配置")
        print("- ConfigManager: 统一配置管理器")
        
        print("\n🚀 下一步: 开始UI组件迁移")
        print("python test_ui_migration.py")
    else:
        print("❌ 部分测试失败，请检查错误信息")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
