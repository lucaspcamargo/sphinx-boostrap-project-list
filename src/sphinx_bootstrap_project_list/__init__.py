from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from docutils import nodes
from docutils.writers.html5_polyglot import HTMLTranslator as html_translator
from jinja2 import Template
from importlib.resources import files
import json
import os

__title__= 'sphinx-bootstrap-project-list'
__license__ = 'GPLv3'
__version__ = '1.0'
__author__ = 'Lucas Pires Camargo'
__url__ = 'https://camargo.eng.br'
__description__ = 'Sphinx extension for rendering nice-looking project lists using Bootstrap 5'
__keywords__ = 'documentation, sphinx, extension, bootstrap, html'


class GenericHTMLNode(nodes.General, nodes.Element):
    """
    A generic HTML node that can be used to render custom HTML content.
    This is a base class for other nodes that need to render HTML.
    """
    @staticmethod
    def html_visit(translator:html_translator, node):
        """
        Visit method for rendering the HTML content of the node.
        This method is called when the node is being processed for HTML output.
        """
        translator.body.append(translator.starttag(node, node['tagname'], **node.get('attributes', {})))
    
    @staticmethod
    def html_depart(translator:html_translator, node):
        """
        Depart method for finalizing the HTML content of the node.
        This method is called after the node has been processed for HTML output.
        """
        translator.body.append("</" + node['tagname'] + ">")


class BSPLNode(nodes.General, nodes.Element):

    @staticmethod
    def html_visit(translator:html_translator, node):


        projects=node.get('projects', {})

        # for pname, pdata in projects.items():
        #     card = GenericHTMLNode(tagname='div', attributes={'class': 'card mb-3 w-100'})
        #     row = GenericHTMLNode(tagname='div', attributes={'class': 'row g-0'})
        #     col = GenericHTMLNode(tagname='div', attributes={'class': 'col-3'})
        #     reldiv = GenericHTMLNode(tagname='div', attributes={'class': 'w-100 h-100 position-relative'})
        #     img_node = nodes.image(rawsource=pdata.get('image_path_rel', None))
        #     img_node['alt'] = pdata.get('image_alt', 'Project Image for ' + pname)
            
        #     reldiv.append(img_node)
        #     col.append(reldiv)
        #     row.append(col)
        #     card.append(row)
        #     append(card)

        template_path = files(__package__).joinpath("templates/project_list.j2")
        template_path = str(template_path)
        with open(template_path, "r", encoding="utf-8") as f:
           template_str = f.read()
        template = Template(template_str)
        translator.body.append(
            template.render(
                projects=projects))

    @staticmethod
    def html_depart(translator, node):
        pass


class BSPLDirective(SphinxDirective):
    option_spec = {
        'json': str 
    }

    has_content = True

    def run(self):
        env = self.state.document.settings.env
        json_file = self.options.get('json', None)
        if json_file:
            with open(json_file, 'r') as f:
                content = json.load(f)
        else:
            raise ValueError("No JSON file provided in options.")

        # TODO: add necessary image and link nodes here
        # during rendering visit, use the generated urls 
        for k,v in content.items():
            if 'image_path' in v:
                image_path = v['image_path']
                v['image_path_rel'] = os.path.join(os.path.dirname(json_file), k, image_path)
                print("[bspl] image_path_rel for", k, "is", v['image_path_rel'])
                
        node = BSPLNode(content=content)
        node['projects'] = content

        return [node]


def setup(app:Sphinx):
    app.add_config_value("bs_proj_list_default_image", None, '')
    app.add_directive('bspl', BSPLDirective)
    app.add_node(BSPLNode, html=(BSPLNode.html_visit, BSPLNode.html_depart))
    app.add_node(GenericHTMLNode, html=(GenericHTMLNode.html_visit, GenericHTMLNode.html_depart))
    
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }