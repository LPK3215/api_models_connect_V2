"""
配置管理服务
提供统一的配置文件操作接口
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import yaml

from backend.core.config_loader import get_providers, refresh_providers
from backend.util import project_root as get_project_root


class ConfigService:
    """配置管理服务"""

    def __init__(self):
        self.project_root = get_project_root()
        self.config_dir = self.project_root / "config"
        self.models_file = self.config_dir / "models.yml"
        self.prompts_dir = self.config_dir / "prompts"
        self.history_file = self.config_dir / "task_history.json"
        self.prompts_dir.mkdir(exist_ok=True)

        # 确保默认提示词存在
        self._ensure_default_prompt()

    def _ensure_default_prompt(self):
        """确保默认提示词文件存在"""
        default_prompt_file = self.prompts_dir / "default.yml"
        if not default_prompt_file.exists():
            from backend.core.config import DEFAULT_PROMPT
            default_content = {
                "name": "默认信息抽取",
                "description": "通用的结构化信息抽取提示词",
                "prompt": DEFAULT_PROMPT,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "tags": ["默认", "信息抽取", "JSON"],
                "category": "通用"
            }
            with open(default_prompt_file, 'w', encoding='utf-8') as f:
                yaml.dump(default_content, f, default_flow_style=False, indent=2, allow_unicode=True)

    # ==================== 模型管理 ====================

    def get_all_providers(self) -> Dict[str, Any]:
        """获取所有云平台信息"""
        return dict(get_providers())

    def get_provider_info(self, provider_key: str) -> Dict[str, Any]:
        """获取指定云平台信息"""
        providers = get_providers()
        if provider_key not in providers:
            raise ValueError(f"云平台 {provider_key} 不存在")
        return providers[provider_key]

    def get_models_by_provider(self, provider_key: str) -> Dict[str, Any]:
        """获取指定云平台的所有模型"""
        provider = self.get_provider_info(provider_key)
        return provider.get("model_pool", {})

    # ==================== 提示词管理 ====================

    def get_all_prompts(self) -> List[Dict[str, Any]]:
        """获取所有提示词"""
        prompts = []
        for prompt_file in self.prompts_dir.glob("*.yml"):
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                data["id"] = prompt_file.stem
                data["file_path"] = str(prompt_file)
                prompts.append(data)
            except Exception:
                continue

        # 按创建时间排序
        prompts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return prompts

    def get_prompt_by_id(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """根据 ID 获取提示词"""
        prompt_file = self.prompts_dir / f"{prompt_id}.yml"
        if not prompt_file.exists():
            return None

        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            data["id"] = prompt_id
            data["file_path"] = str(prompt_file)
            return data
        except Exception:
            return None

    def save_prompt(self, name: str, category: str, description: str, content: str, tags: List[str]) -> Tuple[
        bool, str]:
        """保存提示词"""
        try:
            # 生成文件名（基于名称）
            import re
            safe_name = re.sub(r'[^\w\-_\u4e00-\u9fff]', '_', name)
            prompt_id = safe_name.lower()

            # 检查是否已存在同名文件
            prompt_file = self.prompts_dir / f"{prompt_id}.yml"
            counter = 1
            original_id = prompt_id
            while prompt_file.exists():
                # 检查是否是同一个提示词（通过名称判断）
                try:
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        existing_data = yaml.safe_load(f)
                    if existing_data.get("name") == name:
                        # 更新现有提示词
                        break
                except Exception:
                    pass

                # 生成新的文件名
                prompt_id = f"{original_id}_{counter}"
                prompt_file = self.prompts_dir / f"{prompt_id}.yml"
                counter += 1

            # 准备数据
            now = datetime.now().isoformat()
            prompt_data = {
                "name": name,
                "description": description,
                "category": category,
                "prompt": content,
                "tags": tags,
                "updated_at": now
            }

            # 如果是新文件，添加创建时间
            if not prompt_file.exists():
                prompt_data["created_at"] = now
            else:
                # 保留原有的创建时间
                try:
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        existing_data = yaml.safe_load(f)
                    prompt_data["created_at"] = existing_data.get("created_at", now)
                except Exception:
                    prompt_data["created_at"] = now

            # 保存文件
            with open(prompt_file, 'w', encoding='utf-8') as f:
                yaml.dump(prompt_data, f, default_flow_style=False, indent=2, allow_unicode=True)

            return True, f"提示词 '{name}' 保存成功"

        except Exception as e:
            return False, f"保存失败: {str(e)}"

    def delete_prompt(self, prompt_id: str) -> Tuple[bool, str]:
        """删除提示词"""
        try:
            prompt_file = self.prompts_dir / f"{prompt_id}.yml"
            if not prompt_file.exists():
                return False, "提示词文件不存在"

            # 不允许删除默认提示词
            if prompt_id == "default":
                return False, "不能删除默认提示词"

            # 获取提示词名称用于确认消息
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                prompt_name = data.get("name", prompt_id)
            except Exception:
                prompt_name = prompt_id

            # 删除文件
            prompt_file.unlink()
            return True, f"提示词 '{prompt_name}' 删除成功"

        except Exception as e:
            return False, f"删除失败: {str(e)}"

    # ==================== 系统信息 ====================

    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        import os

        # API 密钥状态
        api_keys = {
            "阿里云 DashScope": "DASHSCOPE_API_KEY",
            "豆包/火山方舟": "ARK_API_KEY",
            "魔塔 ModelScope": "MODELSCOPE_ACCESS_TOKEN",
            "腾讯混元": "HUNYUAN_API_KEY"
        }

        api_status = {}
        for name, env_key in api_keys.items():
            api_status[name] = {
                "configured": bool(os.getenv(env_key)),
                "env_key": env_key
            }

        # 统计信息
        providers = get_providers()
        total_providers = len(providers)
        total_models = sum(len(p["model_pool"]) for p in providers.values())
        total_prompts = len(self.get_all_prompts())

        # 目录状态
        directories = {
            "配置目录": self.config_dir,
            "提示词目录": self.prompts_dir,
            "输入目录": self.project_root / "data" / "inputs",
            "输出目录": self.project_root / "data" / "outputs"
        }

        dir_status = {}
        for name, path in directories.items():
            dir_status[name] = {
                "exists": path.exists(),
                "path": str(path),
                "is_dir": path.is_dir() if path.exists() else False
            }

        return {
            "api_keys": api_status,
            "statistics": {
                "providers": total_providers,
                "models": total_models,
                "prompts": total_prompts
            },
            "directories": dir_status,
            "config_files": {
                "models.yml": self.models_file.exists(),
                "prompts/default.yml": (self.prompts_dir / "default.yml").exists()
            }
        }

    # ==================== 任务历史管理 ====================

    def add_task_record(self, provider: str, model: str, file_count: int,
                        success_count: int, failed_count: int, output_dir: str = None) -> None:
        """添加任务记录"""
        try:
            # 读取现有历史
            history = []
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)

            # 添加新记录
            record = {
                "timestamp": datetime.now().isoformat(),
                "provider": provider,
                "model": model,
                "file_count": file_count,
                "success_count": success_count,
                "failed_count": failed_count,
                "success": failed_count == 0,
                "output_dir": output_dir
            }

            history.insert(0, record)  # 最新的在前面

            # 只保留最近100条记录
            history = history[:100]

            # 保存历史
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

        except Exception:
            # 历史记录失败不影响主要功能
            pass

    def get_task_history(self) -> List[Dict[str, Any]]:
        """获取任务历史"""
        try:
            if not self.history_file.exists():
                return []

            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def get_history_statistics(self) -> Dict[str, Any]:
        """获取历史统计信息"""
        history = self.get_task_history()
        if not history:
            return {
                "total_tasks": 0,
                "success_rate": 0,
                "most_used_provider": "N/A",
                "most_used_model": "N/A",
                "total_files": 0
            }

        # 计算统计信息
        total_tasks = len(history)
        successful_tasks = sum(1 for record in history if record.get("success", False))
        success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # 统计最常用的云平台和模型
        from collections import Counter
        providers = [record.get("provider", "") for record in history if record.get("provider")]
        models = [record.get("model", "") for record in history if record.get("model")]

        most_used_provider = Counter(providers).most_common(1)
        most_used_model = Counter(models).most_common(1)

        total_files = sum(record.get("file_count", 0) for record in history)

        return {
            "total_tasks": total_tasks,
            "success_rate": success_rate,
            "most_used_provider": most_used_provider[0][0] if most_used_provider else "N/A",
            "most_used_model": most_used_model[0][0] if most_used_model else "N/A",
            "total_files": total_files
        }

    def clear_task_history(self) -> Tuple[bool, str]:
        """清空任务历史"""
        try:
            if self.history_file.exists():
                self.history_file.unlink()
            return True, "历史记录已清空"
        except Exception as e:
            return False, f"清空失败: {str(e)}"

    # ==================== 新增模型管理功能 ====================

    def add_model(self, provider_key: str, model_key: str, model_config: Dict[str, Any]) -> Tuple[bool, str]:
        """添加新模型到配置文件"""
        try:
            # 检查云平台是否存在
            providers = get_providers()
            if provider_key not in providers:
                return False, f"云平台 {provider_key} 不存在"

            # 读取现有配置
            if self.models_file.exists():
                with open(self.models_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
            else:
                config_data = {"providers": {}}

            # 确保结构存在
            if "providers" not in config_data:
                config_data["providers"] = {}

            if provider_key not in config_data["providers"]:
                # 从providers复制基本信息
                provider_info = providers[provider_key]["info"].copy()
                config_data["providers"][provider_key] = {
                    "display_name": provider_info["display_name"],
                    "info": {
                        "defaults": provider_info.get("defaults", {})
                    },
                    "models": {}
                }

            if "models" not in config_data["providers"][provider_key]:
                config_data["providers"][provider_key]["models"] = {}

            # 检查模型是否已存在
            if model_key in config_data["providers"][provider_key]["models"]:
                return False, f"模型 {model_key} 已存在，请使用不同的标识符"

            # 添加新模型
            config_data["providers"][provider_key]["models"][model_key] = model_config

            # 保存配置文件
            with open(self.models_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2, allow_unicode=True)

            # 重新加载配置以更新providers缓存
            refresh_providers()

            return True, f"模型 '{model_config['name']}' 添加成功"

        except Exception as e:
            return False, f"添加模型失败: {str(e)}"

    def get_config_manager(self):
        """获取配置管理器（用于缓存清理）"""
        if not hasattr(self, '_config_manager'):
            from backend.core.config_loader import _ConfigManager
            self._config_manager = _ConfigManager()
        return self._config_manager

    # ==================== 默认模型配置 ====================

    def get_default_model(self) -> Optional[Dict[str, str]]:
        """获取默认模型配置（优先级高于上次选择）"""
        try:
            if not self.models_file.exists():
                return None

            with open(self.models_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}

            default_model = config_data.get("default_model")
            if default_model and "provider" in default_model and "model" in default_model:
                # 验证配置的模型是否存在
                providers = get_providers()
                provider_key = default_model["provider"]
                model_key = default_model["model"]

                if provider_key in providers:
                    models = providers[provider_key].get("model_pool", {})
                    if model_key in models:
                        return default_model

            return None
        except Exception:
            return None

    def set_default_model(self, provider_key: str, model_key: str) -> Tuple[bool, str]:
        """设置默认模型"""
        try:
            # 验证模型是否存在
            providers = get_providers()
            if provider_key not in providers:
                return False, f"云平台 {provider_key} 不存在"

            models = providers[provider_key].get("model_pool", {})
            if model_key not in models:
                return False, f"模型 {model_key} 不存在"

            # 读取现有配置
            if self.models_file.exists():
                with open(self.models_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
            else:
                config_data = {}

            # 设置默认模型
            config_data["default_model"] = {
                "provider": provider_key,
                "model": model_key
            }

            # 保存配置
            with open(self.models_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2, allow_unicode=True)

            model_name = models[model_key].get("name", model_key)
            return True, f"默认模型已设置为: {model_name}"
        except Exception as e:
            return False, f"设置失败: {str(e)}"

    def clear_default_model(self) -> Tuple[bool, str]:
        """清除默认模型配置（恢复使用上次选择）"""
        try:
            if not self.models_file.exists():
                return True, "无默认模型配置"

            with open(self.models_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}

            if "default_model" in config_data:
                del config_data["default_model"]

                with open(self.models_file, 'w', encoding='utf-8') as f:
                    yaml.dump(config_data, f, default_flow_style=False, indent=2, allow_unicode=True)

                return True, "默认模型配置已清除，将使用上次选择"

            return True, "无默认模型配置"
        except Exception as e:
            return False, f"清除失败: {str(e)}"

    def get_initial_selection(self) -> Dict[str, str]:
        """获取初始选择（优先默认模型，其次上次选择）"""
        # 1. 优先使用默认模型
        default_model = self.get_default_model()
        if default_model:
            return {
                "provider": default_model["provider"],
                "model": default_model["model"],
                "source": "default"  # 标记来源
            }

        # 2. 其次使用上次选择
        last_choice_file = self.config_dir / "last_choice.json"
        if last_choice_file.exists():
            try:
                with open(last_choice_file, 'r', encoding='utf-8') as f:
                    last_choice = json.load(f)

                # 验证上次选择的模型是否仍然存在
                providers = get_providers()
                provider_key = last_choice.get("provider")
                model_key = last_choice.get("model")

                if provider_key and provider_key in providers:
                    models = providers[provider_key].get("model_pool", {})
                    if model_key and model_key in models:
                        return {
                            "provider": provider_key,
                            "model": model_key,
                            "source": "last_choice"
                        }
            except Exception:
                pass

        # 3. 都没有则返回第一个可用的
        providers = get_providers()
        if providers:
            first_provider = list(providers.keys())[0]
            models = providers[first_provider].get("model_pool", {})
            if models:
                return {
                    "provider": first_provider,
                    "model": list(models.keys())[0],
                    "source": "first_available"
                }

        return {"provider": None, "model": None, "source": "none"}
