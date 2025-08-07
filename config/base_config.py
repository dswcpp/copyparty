"""
配置基类
提供所有配置类的通用功能
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json
import yaml
from pathlib import Path


class ValidationResult:
    """配置验证结果"""
    
    def __init__(self):
        self.is_valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def add_error(self, message: str):
        """添加错误"""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str):
        """添加警告"""
        self.warnings.append(message)
    
    def __bool__(self):
        return self.is_valid


class BaseConfig(ABC):
    """配置基类"""
    
    def __init__(self):
        self._changed = False
        self._validation_rules = {}
    
    @property
    def changed(self) -> bool:
        """配置是否已更改"""
        return self._changed
    
    def mark_changed(self):
        """标记配置已更改"""
        self._changed = True
    
    def mark_saved(self):
        """标记配置已保存"""
        self._changed = False
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        pass
    
    @abstractmethod
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        pass
    
    @abstractmethod
    def get_command_args(self) -> List[str]:
        """生成命令行参数"""
        pass
    
    def validate(self) -> ValidationResult:
        """验证配置"""
        result = ValidationResult()
        
        # 执行基础验证
        self._validate_required_fields(result)
        self._validate_field_types(result)
        self._validate_field_values(result)
        
        # 执行自定义验证
        self._custom_validation(result)
        
        return result
    
    def _validate_required_fields(self, result: ValidationResult):
        """验证必需字段"""
        required_fields = getattr(self, '_required_fields', [])
        config_dict = self.to_dict()
        
        for field in required_fields:
            if field not in config_dict or config_dict[field] is None:
                result.add_error(f"必需字段 '{field}' 缺失或为空")
    
    def _validate_field_types(self, result: ValidationResult):
        """验证字段类型"""
        type_rules = getattr(self, '_type_rules', {})
        config_dict = self.to_dict()
        
        for field, expected_type in type_rules.items():
            if field in config_dict and config_dict[field] is not None:
                if not isinstance(config_dict[field], expected_type):
                    result.add_error(f"字段 '{field}' 类型错误，期望 {expected_type.__name__}")
    
    def _validate_field_values(self, result: ValidationResult):
        """验证字段值"""
        value_rules = getattr(self, '_value_rules', {})
        config_dict = self.to_dict()
        
        for field, rule in value_rules.items():
            if field in config_dict and config_dict[field] is not None:
                value = config_dict[field]
                
                if 'min' in rule and value < rule['min']:
                    result.add_error(f"字段 '{field}' 值 {value} 小于最小值 {rule['min']}")
                
                if 'max' in rule and value > rule['max']:
                    result.add_error(f"字段 '{field}' 值 {value} 大于最大值 {rule['max']}")
                
                if 'choices' in rule and value not in rule['choices']:
                    result.add_error(f"字段 '{field}' 值 '{value}' 不在允许的选择中: {rule['choices']}")
    
    def _custom_validation(self, result: ValidationResult):
        """自定义验证 - 子类可重写"""
        pass
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def from_json(self, json_str: str):
        """从JSON字符串加载"""
        data = json.loads(json_str)
        self.from_dict(data)
    
    def to_yaml(self) -> str:
        """转换为YAML字符串"""
        return yaml.dump(self.to_dict(), default_flow_style=False, allow_unicode=True)
    
    def from_yaml(self, yaml_str: str):
        """从YAML字符串加载"""
        data = yaml.safe_load(yaml_str)
        self.from_dict(data)
    
    def save_to_file(self, file_path: str, format: str = 'json'):
        """保存到文件"""
        path = Path(file_path)
        
        if format.lower() == 'json':
            content = self.to_json()
        elif format.lower() == 'yaml':
            content = self.to_yaml()
        else:
            raise ValueError(f"不支持的格式: {format}")
        
        path.write_text(content, encoding='utf-8')
        self.mark_saved()
    
    def load_from_file(self, file_path: str, format: Optional[str] = None):
        """从文件加载"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
        
        content = path.read_text(encoding='utf-8')
        
        # 自动检测格式
        if format is None:
            if path.suffix.lower() in ['.yaml', '.yml']:
                format = 'yaml'
            else:
                format = 'json'
        
        if format.lower() == 'json':
            self.from_json(content)
        elif format.lower() == 'yaml':
            self.from_yaml(content)
        else:
            raise ValueError(f"不支持的格式: {format}")
        
        self.mark_saved()
    
    def clone(self):
        """克隆配置对象"""
        new_config = self.__class__()
        new_config.from_dict(self.to_dict())
        return new_config
    
    def merge(self, other: 'BaseConfig'):
        """合并另一个配置对象"""
        if not isinstance(other, self.__class__):
            raise TypeError(f"无法合并不同类型的配置: {type(other)}")
        
        other_dict = other.to_dict()
        current_dict = self.to_dict()
        
        # 递归合并字典
        merged_dict = self._merge_dicts(current_dict, other_dict)
        self.from_dict(merged_dict)
        self.mark_changed()
    
    def _merge_dicts(self, dict1: Dict, dict2: Dict) -> Dict:
        """递归合并字典"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_diff(self, other: 'BaseConfig') -> Dict[str, Any]:
        """获取与另一个配置的差异"""
        if not isinstance(other, self.__class__):
            raise TypeError(f"无法比较不同类型的配置: {type(other)}")
        
        current_dict = self.to_dict()
        other_dict = other.to_dict()
        
        return self._get_dict_diff(current_dict, other_dict)
    
    def _get_dict_diff(self, dict1: Dict, dict2: Dict, path: str = "") -> Dict[str, Any]:
        """获取字典差异"""
        diff = {}
        
        # 检查修改和新增
        for key, value in dict2.items():
            current_path = f"{path}.{key}" if path else key
            
            if key not in dict1:
                diff[current_path] = {"action": "added", "value": value}
            elif dict1[key] != value:
                if isinstance(dict1[key], dict) and isinstance(value, dict):
                    nested_diff = self._get_dict_diff(dict1[key], value, current_path)
                    diff.update(nested_diff)
                else:
                    diff[current_path] = {
                        "action": "modified",
                        "old_value": dict1[key],
                        "new_value": value
                    }
        
        # 检查删除
        for key in dict1:
            if key not in dict2:
                current_path = f"{path}.{key}" if path else key
                diff[current_path] = {"action": "removed", "value": dict1[key]}
        
        return diff
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.to_dict()})"
    
    def __repr__(self) -> str:
        return self.__str__()


class ConfigGroup(BaseConfig):
    """配置组 - 包含多个子配置"""
    
    def __init__(self):
        super().__init__()
        self._configs: Dict[str, BaseConfig] = {}
    
    def add_config(self, name: str, config: BaseConfig):
        """添加子配置"""
        self._configs[name] = config
    
    def get_config(self, name: str) -> Optional[BaseConfig]:
        """获取子配置"""
        return self._configs.get(name)
    
    def remove_config(self, name: str):
        """移除子配置"""
        if name in self._configs:
            del self._configs[name]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        for name, config in self._configs.items():
            result[name] = config.to_dict()
        return result
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        for name, config_data in data.items():
            if name in self._configs:
                self._configs[name].from_dict(config_data)
    
    def get_command_args(self) -> List[str]:
        """生成命令行参数"""
        args = []
        for config in self._configs.values():
            args.extend(config.get_command_args())
        return args
    
    def validate(self) -> ValidationResult:
        """验证所有子配置"""
        result = ValidationResult()
        
        for name, config in self._configs.items():
            config_result = config.validate()
            if not config_result:
                for error in config_result.errors:
                    result.add_error(f"{name}: {error}")
                for warning in config_result.warnings:
                    result.add_warning(f"{name}: {warning}")
        
        return result
    
    @property
    def changed(self) -> bool:
        """检查是否有任何子配置更改"""
        return any(config.changed for config in self._configs.values())
