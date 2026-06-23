class NoneError(Exception):
    def __init__(self, error_message="Object not constructed. Cannot access a 'None' object."):
        self.message = error_message
        super().__init__(self.error_message)


class InsertingIntoDBError(Exception):
    def __init__(self, error_message="Insertion ERROR, please check the data types"):
        self.error_message = error_message
        super().__init__(self.error_message)
