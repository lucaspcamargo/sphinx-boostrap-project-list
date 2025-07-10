from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from docutils import nodes
from docutils.writers.html5_polyglot import HTMLTranslator as html_translator
from jinja2 import Template
from importlib.resources import files
import json
import posixpath
import urllib.parse as urlparse
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
        """
        Visit method for rendering the BSPLNode content.
        This method is called when the node is being processed for HTML output.
        It extracts project information from the node's children and renders it using a Jinja2 template.
        """
        projects=node.get('projects', {})

        # go over child nodes and extract image and link uris
        # store in projects dict
        for child in node.children:
            if isinstance(child, nodes.image):
                olduri = child['uri']
                if olduri in translator.builder.images:
                    child['uri'] = posixpath.join(
                        translator.builder.imgpath, urlparse.quote(translator.builder.images[olduri])
                    )
                proj_key = child.get('proj_key', None)
                if proj_key and proj_key in projects:
                    projects[proj_key]['image_path_rel'] = child['uri']
                    projects[proj_key]['image_alt'] = child.get('alt', 'Project Image for ' + proj_key)
                else:
                    print("[bspl] Warning: image node with proj_key", proj_key, "not found in projects dict")
            elif isinstance(child, nodes.TextElement) and len(child.children) == 1 and isinstance(child.children[0], nodes.reference):
                refnode = child.children[0]
                proj_key = refnode.get('proj_key', None)
                if proj_key and proj_key in projects:
                    projects[proj_key]['index_url'] = refnode['refuri']
                    projects[proj_key]['nice_title'] = refnode.astext()
                else:
                    print("[bspl] Warning: reference node with proj_key", proj_key, "not found in projects dict")
            else:
                print("[bspl] Warning: unhandled child node type", type(child), "in BSPLNode.html_visit")


        template_path = files(__package__).joinpath("templates/project_list.j2")
        template_path = str(template_path)
        with open(template_path, "r", encoding="utf-8") as f:
           template_str = f.read()
        template = Template(template_str)
        translator.body.append(
            template.render(
                projects=projects))
        
        # ignore children and don't even depart node
        # we are done
        raise nodes.SkipNode

    @staticmethod
    def html_depart(translator, node):
        raise RuntimeError("BSPLNode.html_depart should not be called, as we raise SkipNode in html_visit.")


def TextualVisit(writer, node):
    # only keep link children, more precisely the wrappers, they shall be rendered as-is
    all_children = list(node.children[:])
    node.children.clear()
    all_text_children = [ch for ch in all_children if isinstance(ch, nodes.TextElement)]
    node.children = all_text_children


def TextualDepart(writer, node):
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
                

        # initialize image urls
        for k, v in content.items():
            v['image_path_rel'] = None
            v['index_path_rel'] = None
            v['nice_title'] = v.get('nice_title', k)
            v['descr'] = v.get('descr', 'No description available.')
            v['last_mod_fmt'] = v.get('last_mod_fmt', 'Unknown date')
            if 'image_path' not in v:
                v['image_path'] = env.config.bspl_default_image or '/_static/proj_default.png'
            if 'index_path' not in v:
                v['index_path'] = k + '.md'

        node = BSPLNode(content=content)


        # add necessary image and link nodes here
        # during rendering visit, use the generated urls 
        for k,v in content.items():
            if 'image_path' in v:
                image_path = v['image_path']
                v['image_path_rel'] = os.path.join(os.path.dirname(json_file), image_path) if not (image_path.startswith('http') or image_path.startswith('/')) else image_path
                print("[bspl] image_path_rel for", k, "is", v['image_path_rel'])
                img_node = nodes.image(rawsource=v['image_path_rel'])
                img_node['uri'] = v['image_path_rel']
                img_node['alt'] = v.get('image_alt', 'Project Image for ' + k)
                img_node["proj_key"] = k
                node.append(img_node)
            if 'index_path' in v:
                index_path = v['index_path']
                if index_path.endswith('.md'):
                    index_path = index_path[:-3] + ".html"
                v['index_path_rel'] = os.path.join(os.path.dirname(json_file), index_path)
                print("[bspl] index_path_rel for", k, "is", v['index_path_rel'])
                link_node = nodes.reference(rawsource=v['index_path_rel'], text=v.get('nice_title', k), refuri=v['index_path_rel'])
                link_node['proj_key'] = k
                wrap_p = nodes.paragraph(proj_key=k)
                wrap_p.append(link_node)
                node.append(wrap_p)

        node['projects'] = content

        return [node]


def setup(app:Sphinx):
    app.add_config_value("bspl_default_image", None, '')
    app.add_directive('bspl', BSPLDirective)
    app.add_node(BSPLNode, 
                 html=(BSPLNode.html_visit, BSPLNode.html_depart),
                 text=(TextualVisit, TextualDepart), 
                 gemini=(TextualVisit, TextualDepart),
                 latex=(TextualVisit, TextualDepart),
    )
    
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }