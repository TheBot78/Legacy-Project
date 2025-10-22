services = {}

def register_service(name: str):
    def decorator(func):
        services[name] = func
        return func
    return decorator

def call_service(name: str, params: dict):
    if name not in services:
        raise ValueError(f"Unknown method: {name}")
    return services[name](**params)
