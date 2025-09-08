# Copyright (c) 1998-2007 INRIA
# Python rewrite of Geneweb plugin system

import os
import sys
import importlib
import inspect
from typing import Dict, List, Any, Callable, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class PluginInfo:
    """Plugin information"""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    enabled: bool = True

class GenewebPlugin(ABC):
    """Base class for Geneweb plugins"""
    
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """Get plugin information"""
        pass
    
    @abstractmethod
    def initialize(self, context: Dict[str, Any]):
        """Initialize plugin"""
        pass
    
    @abstractmethod
    def finalize(self):
        """Cleanup plugin"""
        pass
    
    def get_hooks(self) -> Dict[str, Callable]:
        """Get plugin hooks"""
        return {}
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """Get web routes provided by plugin"""
        return []
    
    def get_templates(self) -> Dict[str, str]:
        """Get template overrides"""
        return {}

class PluginManager:
    """Manage Geneweb plugins"""
    
    def __init__(self, plugin_dir: str):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, GenewebPlugin] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        self.routes: List[Dict[str, Any]] = []
        self.templates: Dict[str, str] = {}
        
        # Add plugin directory to Python path
        if plugin_dir not in sys.path:
            sys.path.insert(0, plugin_dir)
    
    def load_plugins(self):
        """Load all plugins from plugin directory"""
        if not os.path.exists(self.plugin_dir):
            return
        
        for item in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, item)
            
            if os.path.isdir(plugin_path):
                self._load_plugin_from_directory(item, plugin_path)
            elif item.endswith('.py') and not item.startswith('_'):
                self._load_plugin_from_file(item[:-3], plugin_path)
    
    def _load_plugin_from_directory(self, plugin_name: str, plugin_path: str):
        """Load plugin from directory"""
        init_file = os.path.join(plugin_path, '__init__.py')
        if not os.path.exists(init_file):
            return
        
        try:
            module = importlib.import_module(plugin_name)
            self._register_plugin_from_module(plugin_name, module)
        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")
    
    def _load_plugin_from_file(self, plugin_name: str, plugin_path: str):
        """Load plugin from single file"""
        try:
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._register_plugin_from_module(plugin_name, module)
        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")
    
    def _register_plugin_from_module(self, plugin_name: str, module):
        """Register plugin from loaded module"""
        # Find plugin class
        plugin_class = None
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, GenewebPlugin) and 
                obj != GenewebPlugin):
                plugin_class = obj
                break
        
        if not plugin_class:
            print(f"No plugin class found in {plugin_name}")
            return
        
        # Instantiate plugin
        try:
            plugin = plugin_class()
            info = plugin.get_info()
            
            if info.enabled:
                self.plugins[plugin_name] = plugin
                self._register_plugin_hooks(plugin)
                self._register_plugin_routes(plugin)
                self._register_plugin_templates(plugin)
                
                print(f"Loaded plugin: {info.name} v{info.version}")
        except Exception as e:
            print(f"Error instantiating plugin {plugin_name}: {e}")
    
    def _register_plugin_hooks(self, plugin: GenewebPlugin):
        """Register plugin hooks"""
        hooks = plugin.get_hooks()
        for hook_name, hook_func in hooks.items():
            if hook_name not in self.hooks:
                self.hooks[hook_name] = []
            self.hooks[hook_name].append(hook_func)
    
    def _register_plugin_routes(self, plugin: GenewebPlugin):
        """Register plugin routes"""
        routes = plugin.get_routes()
        self.routes.extend(routes)
    
    def _register_plugin_templates(self, plugin: GenewebPlugin):
        """Register plugin templates"""
        templates = plugin.get_templates()
        self.templates.update(templates)
    
    def initialize_plugins(self, context: Dict[str, Any]):
        """Initialize all loaded plugins"""
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.initialize(context)
            except Exception as e:
                print(f"Error initializing plugin {plugin_name}: {e}")
    
    def finalize_plugins(self):
        """Finalize all plugins"""
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.finalize()
            except Exception as e:
                print(f"Error finalizing plugin {plugin_name}: {e}")
    
    def call_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Call all functions registered for a hook"""
        results = []
        if hook_name in self.hooks:
            for hook_func in self.hooks[hook_name]:
                try:
                    result = hook_func(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    print(f"Error calling hook {hook_name}: {e}")
        return results
    
    def get_plugin_routes(self) -> List[Dict[str, Any]]:
        """Get all plugin routes"""
        return self.routes
    
    def get_plugin_templates(self) -> Dict[str, str]:
        """Get all plugin templates"""
        return self.templates
    
    def get_plugin_info(self) -> List[PluginInfo]:
        """Get information about all loaded plugins"""
        return [plugin.get_info() for plugin in self.plugins.values()]
