#def data(entity) -> Callable[[Any], Optional[List[types.Data]]]:
def data(entity): # TODO: add static typing(Protocol)
    def fn(*args, **kwargs):
        assert entity.valid(*args, **kwargs)
        loaded = entity.load(*args, **kwargs)
        processed = entity.process(loaded)
        return entity.canonical(processed)
    return fn

def dataset(entity):
    def fn(*args, **kwargs):
        assert entity.valid(*args, **kwargs)
        loaded_rels = entity.load(*args, **kwargs)
        selected = entity.select(loaded_rels)
        return entity.canonical(selected)
    return fn
