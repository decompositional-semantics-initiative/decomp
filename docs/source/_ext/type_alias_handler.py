"""
Custom Sphinx extension to handle PEP 695 type aliases.

This is a temporary workaround until Sphinx fully supports PEP 695.
"""

from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from docutils import nodes
from docutils.parsers.rst import directives


class TypeAliasDirective(SphinxDirective):
    """Directive to document type aliases."""
    
    has_content = True
    required_arguments = 1
    option_spec = {
        'type': directives.unchanged,
        'module': directives.unchanged,
    }
    
    def run(self):
        name = self.arguments[0]
        module = self.options.get('module', '')
        type_def = self.options.get('type', '')
        
        # Create the signature
        if module:
            full_name = f"{module}.{name}"
        else:
            full_name = name
            
        sig_node = nodes.paragraph()
        sig_node += nodes.strong(text='type ')
        sig_node += nodes.literal(text=f"{name} = {type_def}")
        
        # Add description if provided
        content_node = nodes.paragraph()
        if self.content:
            self.state.nested_parse(self.content, self.content_offset, content_node)
        
        # Create a definition list
        dl = nodes.definition_list()
        dli = nodes.definition_list_item()
        dt = nodes.term()
        dt += sig_node
        dd = nodes.definition()
        dd += content_node
        
        dli += dt
        dli += dd
        dl += dli
        
        return [dl]


def setup(app: Sphinx):
    """Setup the extension."""
    app.add_directive('typealias', TypeAliasDirective)
    
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }