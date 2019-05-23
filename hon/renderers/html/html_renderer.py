from hon.markdown import Markdown
from ..renderer import Renderer

class HtmlRenderer(Renderer):

    _name = 'html'

    #: The default configuration state for the HTML renderer, this is loaded
    #: into the application configuration.
    default_config = {
        'theme': None,

        #: The default theme to use, defaults to 'light'
        'default_theme': 'light',

        #: Use "smart quotes" instead of the usual `"` character.
        'curly_quotes': True,

        #: Should mathjax be enabled?
        #'mathjax_support': bool,
    
        #: An optional google analytics code.
        'google_analytics': None,
        
        #: Additional CSS stylesheets to include in the rendered page's
        #: `<head>`.
        'additional_css': [],
    
        #: Additional JS scripts to include at the bottom of the rendered page's
        #: `<body>`.
        'additional_js': [],
    
        # Don't render section labels.
        # 'no_section_label': False,
    
        # Search settings. If `None`, the default will be used.
        # pub search: Option<Search>,
        # /// Git repository url. If `None`, the git button will not be shown.
        # pub git_repository_url: Option<String>,
        # /// FontAwesome icon class to use for the Git repository link.
        # /// Defaults to `fa-github` if `None`.
        # pub git_repository_icon: Option<String>,
    }

    @property
    def livereload_url(self):
        return None
    
    def on_finish(self, book):
        print('in finish')

    def on_generate_pages(self, book):
        print('evaluating book results')
        for item in book.items:
            print(item.text)

    def on_init(self, book):
        pass
    
    def on_render_page(self, page, book):
        raw_text = str(page.raw_text)
        md = Markdown()
        markedup_text = md.convert(raw_text)

        if markedup_text:
            page.text = markedup_text
