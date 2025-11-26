class DependencyNotRegistered(Exception):
    def __init__(self, detail: str):
        super().__init__(detail)