import inspect


def forward_partial_args(func):
    def func_wrapper(**kw):
        signature = inspect.signature(func)
        kw = {k: v for k, v in kw.items() if k in signature.parameters}
        func(**kw)

    return func_wrapper
