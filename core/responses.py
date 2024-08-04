from rest_framework.response import Response
from rest_framework import status


class ValidationErrorResponse(Response):
    def __init__(
        self,
        validations: dict,
        msg: str = "Error en validaciones",
        status: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(
            data={"msg": msg, "validations": validations},
            status=status,
        )
