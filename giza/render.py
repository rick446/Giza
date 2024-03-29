#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Adds a couple of nice renderers'''
import json

import pkg_resources
from zope.interface import implements
from pyramid.interfaces import ITemplateRenderer

try:
    import ew.render
    from ew import kajiki_ew
except ImportError:
    ew = None

class JSONRenderer(object):
    def __init__(self, info): 
        """ Constructor: info will be an object having the the 
        following attributes: name (the renderer name), package 
        (the package that was 'current' at the time the 
        renderer was registered), type (the renderer type 
        name), registry (the current application registry) and 
        settings (the deployment settings dictionary).  """ 

    def __call__(self, value, system): 
        """ Call a the renderer implementation with the value 
        and the system value passed in as arguments and return 
        the result (a string or unicode object).  The value is 
        the return value of a view.      The system value is a 
        dictionary containing available system values 
        (e.g. view, context, and request). """ 
        request = system.get('request')
        response = request.response
        if response is not None: 
            response.content_type = 'application/json' 
        return json.dumps(value, default=self._default)

    @staticmethod
    def _default(value):
        if hasattr(value, '__json__'):
            return value.__json__()
        raise TypeError, value
        
if ew is not None:
    class EWTemplateRenderer(object):
        implements(ITemplateRenderer)

        def __init__(self, info):
            pass

        @property
        def resource_manager(self):
            return ew.widget_context.resource_manager

        def implementation(self): # pragma no cover
            return self

        def __call__(self, value, system):
            """ ``value`` is the result of the view.
            Returns a result (a string or unicode object useful as a
            response body). Values computed by the system are passed in the
            ``system`` parameter, which is a dictionary containing:

            * ``view`` (the view callable that returned the value),
            * ``renderer_name`` (the template name or simple name of the renderer),
            * ``context`` (the context object passed to the view), and
            * ``request`` (the request object passed to the view).
            """
            template, engine_name = system['renderer_name'].rsplit('.', 1)
            engine = ew.render.TemplateEngine.get_engine(engine_name)
            Template = engine.load(template, is_fragment=False)
            context = dict(system)
            context.update(renderer=self)

            context.update(value)
            return engine.render(Template, context)

        def register_css(self, href, **kw):
            self.resource_manager.register(kajiki_ew.CSSLink(href, **kw))

        def register_js(self, href, **kw):
            self.resource_manager.register(kajiki_ew.JSLink(href, **kw))

        def emit(self, region):
            return self.resource_manager.emit(region)

    def enable_ew(config):
        '''Sets up the Kajiki templating language for the specified
        file extensions.
        '''
        for ep in pkg_resources.iter_entry_points('easy_widgets.engines'):
            config.add_renderer('.' + ep.name, EWTemplateRenderer)
