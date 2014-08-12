"""Base class for UFL expression multifunctions."""

# Copyright (C) 2008-2014 Martin Sandve Alnes
#
# This file is part of UFL.
#
# UFL is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UFL is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with UFL. If not, see <http://www.gnu.org/licenses/>.


from ufl.log import error
from ufl.core.expr import Expr

class MultiFunction(object):
    """Base class for collections of nonrecursive expression node handlers."""
    _handlers_cache = {}
    def __init__(self):
        # Analyse class properties and cache handler data the
        # first time this is run for a particular class
        algorithm_class = type(self).__name__
        cache_data = MultiFunction._handlers_cache.get(algorithm_class)
        if not cache_data:
            cache_data = [None]*len(Expr._ufl_all_classes_)
            # For all UFL classes
            for classobject in Expr._ufl_all_classes_:
                # Iterate over the inheritance chain
                # (NB! This assumes that all UFL classes inherits from
                # a single Expr subclass and that the first superclass
                # is always from the UFL Expr hierarchy!)
                for c in classobject.mro():
                    # Register classobject with handler for the first encountered superclass
                    name = c._ufl_handler_name_
                    if getattr(self, name, None):
                        cache_data[classobject._ufl_typecode_] = name
                        break
            MultiFunction._handlers_cache[algorithm_class] = cache_data
        # Build handler list for this particular class (get functions bound to self)
        self._handlers = [getattr(self, name) for name in cache_data]

    def __call__(self, o, *args, **kwargs):
        return self._handlers[o._ufl_typecode_](o, *args, **kwargs)

    def undefined(self, o):
        "Trigger error."
        error("No handler defined for %s." % o._ufl_class_.__name__)

    # Set default behaviour for any Expr
    expr = undefined