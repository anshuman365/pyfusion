"""
Template engine for PyFusion
"""
import os
import re
from typing import Any, Dict, Callable
from ..core.exceptions import PyFusionError
from ..core.logging import log

class TemplateEngine:
    """Simple template engine with variable substitution and basic control structures"""
    
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = template_dir
        self.filters: Dict[str, Callable] = {}
        self._setup_builtin_filters()
    
    def _setup_builtin_filters(self):
        """Setup built-in template filters"""
        self.filters.update({
            'upper': str.upper,
            'lower': str.lower,
            'title': str.title,
            'length': len,
            'first': lambda x: x[0] if x else None,
            'last': lambda x: x[-1] if x else None,
            'join': lambda x, sep=',': sep.join(str(i) for i in x),
            'default': lambda x, default='': x if x is not None else default,
        })
    
    def register_filter(self, name: str, filter_func: Callable):
        """Register custom template filter"""
        self.filters[name] = filter_func
    
    def render(self, template_name: str, context: Dict[str, Any] = None) -> str:
        """Render template with context"""
        if context is None:
            context = {}
        
        template_path = os.path.join(self.template_dir, template_name)
        
        if not os.path.exists(template_path):
            raise PyFusionError(f"Template not found: {template_path}")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self._process_template(content, context)
        except Exception as e:
            raise PyFusionError(f"Error rendering template: {e}")
    
    def _process_template(self, content: str, context: Dict[str, Any]) -> str:
        """Process template content with context"""
        # Handle includes
        content = self._process_includes(content)
        
        # Handle blocks and extends (simple version)
        content = self._process_blocks(content)
        
        # Handle variables
        content = self._process_variables(content, context)
        
        # Handle for loops
        content = self._process_loops(content, context)
        
        # Handle conditionals
        content = self._process_conditionals(content, context)
        
        return content
    
    def _process_includes(self, content: str) -> str:
        """Process include statements"""
        pattern = r'{%\s*include\s+[\'"]([^\'"]+)[\'"]\s*%}'
        
        def replace_include(match):
            include_file = match.group(1)
            include_path = os.path.join(self.template_dir, include_file)
            
            if os.path.exists(include_path):
                with open(include_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                log.warning(f"Include file not found: {include_path}")
                return ""
        
        return re.sub(pattern, replace_include, content)
    
    def _process_blocks(self, content: str) -> str:
        """Process block statements (simplified)"""
        # Simple block implementation - in full version would handle extends
        pattern = r'{%\s*block\s+(\w+)\s*%}(.*?){%\s*endblock\s*%}'
        return re.sub(pattern, r'\2', content, flags=re.DOTALL)
    
    def _process_variables(self, content: str, context: Dict[str, Any]) -> str:
        """Process variable substitutions with filters"""
        pattern = r'{{\s*([^}|]+)(?:\s*\|\s*(\w+)(?::([^}]+))?)?\s*}}'
        
        def replace_variable(match):
            var_path = match.group(1).strip()
            filter_name = match.group(2)
            filter_arg = match.group(3)
            
            # Get variable value
            value = self._get_nested_value(context, var_path)
            
            # Apply filter if specified
            if filter_name and filter_name in self.filters:
                if filter_arg:
                    value = self.filters[filter_name](value, filter_arg)
                else:
                    value = self.filters[filter_name](value)
            
            return str(value) if value is not None else ""
        
        return re.sub(pattern, replace_variable, content)
    
    def _process_loops(self, content: str, context: Dict[str, Any]) -> str:
        """Process for loops"""
        pattern = r'{%\s*for\s+(\w+)\s+in\s+([^%]+)\s*%}(.*?){%\s*endfor\s*%}'
        
        def replace_loop(match):
            var_name = match.group(1)
            iterable_expr = match.group(2).strip()
            loop_content = match.group(3)
            
            # Get iterable from context
            iterable = self._get_nested_value(context, iterable_expr)
            
            if not iterable or not hasattr(iterable, '__iter__'):
                return ""
            
            result = []
            for index, item in enumerate(iterable):
                # Create loop context
                loop_context = {
                    var_name: item,
                    'loop': {
                        'index': index + 1,
                        'index0': index,
                        'first': index == 0,
                        'last': index == len(iterable) - 1,
                        'length': len(iterable)
                    }
                }
                
                # Process loop content with item context
                item_content = self._process_variables(loop_content, {**context, **loop_context})
                result.append(item_content)
            
            return ''.join(result)
        
        return re.sub(pattern, replace_loop, content, flags=re.DOTALL)
    
    def _process_conditionals(self, content: str, context: Dict[str, Any]) -> str:
        """Process if statements"""
        pattern = r'{%\s*if\s+([^%]+)\s*%}(.*?)(?:{%\s*else\s*%}(.*?))?{%\s*endif\s*%}'
        
        def replace_conditional(match):
            condition = match.group(1).strip()
            if_content = match.group(2)
            else_content = match.group(3) or ""
            
            # Evaluate condition (simplified)
            condition_value = self._evaluate_condition(condition, context)
            
            if condition_value:
                return if_content
            else:
                return else_content
        
        return re.sub(pattern, replace_conditional, content, flags=re.DOTALL)
    
    def _get_nested_value(self, context: Dict[str, Any], path: str) -> Any:
        """Get nested value from context using dot notation"""
        parts = path.split('.')
        value = context
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return None
        
        return value
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate condition string (simplified)"""
        # Handle simple comparisons
        if '==' in condition:
            left, right = condition.split('==', 1)
            left_val = self._get_nested_value(context, left.strip())
            right_val = self._get_nested_value(context, right.strip()) or right.strip().strip('"\'')
            return str(left_val) == str(right_val)
        
        elif '!=' in condition:
            left, right = condition.split('!=', 1)
            left_val = self._get_nested_value(context, left.strip())
            right_val = self._get_nested_value(context, right.strip()) or right.strip().strip('"\'')
            return str(left_val) != str(right_val)
        
        else:
            # Treat as truthy check
            value = self._get_nested_value(context, condition.strip())
            return bool(value)

# Example usage with WebServer integration
class TemplateMixin:
    """Mixin to add template support to WebServer"""
    
    def __init__(self):
        self.template_engine = TemplateEngine()
    
    def render_template(self, template_name: str, **context):
        """Render template with context"""
        from flask import render_template_string
        template_content = self.template_engine.render(template_name, context)
        return render_template_string(template_content)