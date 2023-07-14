from anilibria import HTTPException


class AnilibriaAgentException(HTTPException):
    pass


class CantFindAnilibriaMirror(AnilibriaAgentException):
    pass


class ResourceDownloadingFailed(AnilibriaAgentException):
    pass
