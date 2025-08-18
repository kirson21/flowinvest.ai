"""
CGI compatibility shim for Python 3.13+
The cgi module was removed in Python 3.13, but some dependencies still try to import it.
This provides basic compatibility.
"""
import sys
from urllib.parse import parse_qs

# Only create the shim if cgi module doesn't exist
try:
    import cgi
except ImportError:
    print("⚠️ CGI module not found, creating compatibility shim...")
    
    class FieldStorage:
        """Basic FieldStorage replacement"""
        def __init__(self, *args, **kwargs):
            self.list = []
            self.file = None
            
        def getvalue(self, key, default=None):
            return default
            
        def getlist(self, key):
            return []
    
    # Create a mock cgi module
    class CGIModule:
        FieldStorage = FieldStorage
        
        @staticmethod
        def parse_qs(*args, **kwargs):
            return parse_qs(*args, **kwargs)
            
        @staticmethod
        def escape(s, quote=False):
            """Escape HTML special characters"""
            s = s.replace("&", "&amp;")
            s = s.replace("<", "&lt;")
            s = s.replace(">", "&gt;")
            if quote:
                s = s.replace('"', "&quot;")
                s = s.replace("'", "&#x27;")
            return s
    
    # Add the mock module to sys.modules
    sys.modules['cgi'] = CGIModule()
    print("✅ CGI compatibility shim installed")