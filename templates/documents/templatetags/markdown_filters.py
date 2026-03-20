from django import template
import re

register = template.Library()

@register.filter
def clean_markdown(value):
    """Remove markdown formatting from text"""
    if not value:
        return value
    
    # Convert to string if not already
    value = str(value)
    
    # Remove bold markdown
    value = value.replace('**', '')
    value = value.replace('*', '')
    
    # Remove markdown headers
    value = value.replace('#', '')
    
    # Clean up multiple newlines
    value = re.sub(r'\n\s*\n', '\n\n', value)
    
    # Remove extra spaces at start and end of lines
    lines = [line.strip() for line in value.split('\n')]
    value = '\n'.join(lines)
    
    return value.strip()