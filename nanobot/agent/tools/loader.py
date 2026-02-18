"""
Tool loader for dynamic tool loading.
"""

import importlib
import inspect
from pathlib import Path
from typing import List, Type

from loguru import logger
from nanobot.agent.tools.base import Tool


def load_tools(tool_paths: List[str]) -> List[Tool]:
    """
    Load tool classes from dot-notation paths.
    
    Args:
        tool_paths: List of strings like "my_module.MyTool"
        
    Returns:
        List of instantiated Tool objects.
    """
    tools: List[Tool] = []
    
    for path in tool_paths:
        try:
            if "." not in path:
                logger.warning(f"Invalid tool path '{path}': must be 'module.ClassName'")
                continue
                
            module_name, class_name = path.rsplit(".", 1)
            
            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                logger.warning(f"Failed to import tool module '{module_name}': {e}")
                continue
                
            if not hasattr(module, class_name):
                logger.warning(f"Module '{module_name}' has no class '{class_name}'")
                continue
                
            tool_class = getattr(module, class_name)
            
            if not inspect.isclass(tool_class) or not issubclass(tool_class, Tool):
                logger.warning(f"'{path}' is not a subclass of Tool")
                continue
                
            # Instantiate the tool (assume no-arg constructor for custom tools for now)
            # If complex init is needed, we might need a factory pattern or config injection
            try:
                tool_instance = tool_class()
                tools.append(tool_instance)
                logger.info(f"Loaded custom tool: {tool_instance.name}")
            except Exception as e:
                logger.warning(f"Failed to instantiate tool '{class_name}': {e}")
                
        except Exception as e:
            logger.error(f"Error loading tool '{path}': {e}")
            
    return tools
