class InteractionError(Exception):
    pass


class OutOfSync(InteractionError):
    pass


class ConverterFailed(InteractionError):
    def __init__(self, value):
        super().__init__(value)
        self.value = value


class NotASnowflake(ConverterFailed):
    pass
