class AniTogetherError(Exception):
    code: int
    message: str

    def __init__(self):
        super().__init__(f"[{self.code}] {self.message}")


class RoomDoesNotExists(AniTogetherError):
    code = 1
    message = "Room does not exist"


class UserNotAMemberOfRoom(AniTogetherError):
    code = 2
    message = "User not a member of room"


class UnknownCommand(AniTogetherError):
    code = 3
    message = "Unknown command"


class IncorrectMessage(AniTogetherError):
    code = 4
    message = "Incorrect message"


class ParamNotPassed(AniTogetherError):
    code = 5
    message = "{param_name} not passed"

    def __init__(self, param_name: str):
        self.param_name = param_name
        self.message = self.message.format(param_name=param_name)
        super().__init__()


class NotCompatibleVersion(AniTogetherError):
    code = 6
    message = "Your version is not supported"
