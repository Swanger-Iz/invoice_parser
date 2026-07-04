class NoneError(Exception):
    def __init__(self, error_message="Object not constructed. Cannot access a 'None' object."):
        self.message = error_message
        super().__init__(self.error_message)


class InsertingIntoDBError(Exception):
    def __init__(self, error_message="Insertion ERROR, please check the data types"):
        self.error_message = error_message
        super().__init__(self.error_message)


class ModelServerError(Exception):
    def __init__(self, error_message="AI Service is unable now, please try later"):
        self.error_message = error_message
        super().__init__(self.error_message)


class UnknownModelCallingError(Exception):
    def __init__(self, error_message="Unknown Model Calling Error"):
        self.error_message = error_message
        super().__init__(self.error_message)
