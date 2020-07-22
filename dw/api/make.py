def data(entity):
    def fn(root):
        checked = entity.check(root)
        loaded = entity.load(checked)
        processed = entity.process(checked)
        return entity.canonical(processed)
