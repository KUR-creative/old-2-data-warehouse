from typing import List, Callable, Any, Optional

from dw.const import types


#def data(entity) -> Callable[[Any], Optional[List[types.Data]]]:
def data(entity):
    def fn(root):
        assert entity.valid(root)
        loaded = entity.load(root)
        processed = entity.process(loaded)
        return entity.canonical(processed)
    return fn
