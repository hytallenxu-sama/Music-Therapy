import pkgutil
import importlib

__all__ = []  # Explicitly track imported symbols

# Dynamically import all submodules in the 'modules' package
__path__ = pkgutil.extend_path(__path__, __name__)
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__, prefix=__name__ + "."):
    module = importlib.import_module(module_name)
    for attribute_name in dir(module):
        # Skip private/internal attributes
        if not attribute_name.startswith("_"):
            # Expose the attribute at the package level
            globals()[attribute_name] = getattr(module, attribute_name)
            __all__.append(attribute_name)  # Add the symbol to __all__
