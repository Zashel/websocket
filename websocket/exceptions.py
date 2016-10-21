class RecievedNotString(Exception):
    def __init__(self, message_type):
        self._type = message_type
        if message_type == 2:
            message = "Got Blob, expected String"
        elif message_type == 3:
            message = "Got ByteArray, expected String"
        else:
            message = "Received code {}".format(str(message_type))
        super().__init__(message)

    @property
    def type(self):
        return self._type
