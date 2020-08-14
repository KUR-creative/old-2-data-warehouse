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
        loaded = entity.load(*args, **kwargs)
        selected = entity.select(loaded)
        return entity.canonical(selected)
    return fn

def output(entity):
    def fn(*args, **kwargs):
        assert entity.valid(*args, **kwargs)
        loaded = entity.load(*args, **kwargs)
        generated = entity.generate(loaded)
        return entity.canonical(generated)
    return fn
