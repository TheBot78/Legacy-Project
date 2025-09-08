# Example plugin for Geneweb

from .plugin_manager import GenewebPlugin, PluginInfo
from typing import Dict, Any, List, Callable

class ExamplePlugin(GenewebPlugin):
    """Example plugin demonstrating the plugin system"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="Example Plugin",
            version="1.0.0",
            description="An example plugin for demonstration",
            author="Geneweb Team",
            dependencies=[]
        )
    
    def initialize(self, context: Dict[str, Any]):
        """Initialize the plugin"""
        self.database = context.get('database')
        print("Example plugin initialized")
    
    def finalize(self):
        """Cleanup the plugin"""
        print("Example plugin finalized")
    
    def get_hooks(self) -> Dict[str, Callable]:
        """Register hooks"""
        return {
            'person_display': self.enhance_person_display,
            'search_results': self.filter_search_results
        }
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """Register web routes"""
        return [
            {
                'path': '/plugin/example',
                'method': 'GET',
                'handler': self.handle_example_page
            }
        ]
    
    def get_templates(self) -> Dict[str, str]:
        """Register template overrides"""
        return {
            'example.html': '''
{% extends "base.html" %}
{% block content %}
<h1>Example Plugin Page</h1>
<p>This page is provided by the example plugin.</p>
{% endblock %}
'''
        }
    
    def enhance_person_display(self, person, context):
        """Hook to enhance person display"""
        # Add additional information to person display
        context['plugin_info'] = "Enhanced by Example Plugin"
        return context
    
    def filter_search_results(self, results):
        """Hook to filter search results"""
        # Example: filter out private persons
        return [r for r in results if r.get('access') != 'private']
    
    def handle_example_page(self, request):
        """Handle example page request"""
        return {
            'template': 'example.html',
            'context': {
                'message': 'Hello from Example Plugin!'
            }
        }
