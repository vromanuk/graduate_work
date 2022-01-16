import functools
from abc import abstractmethod
from typing import Type

from flask import Response

from src import uapi
from src.constants import PROTOBUF_MIMETYPE
from src.protobuf.common_pb2 import Error as ErrorProto
from src.protobuf.user_pb2 import UserInfoRequest as UserInfoRequestProto
from src.protobuf.user_pb2 import UserInfoResponse as UserInfoResponseProto


class ProtobufType:
    """A general protobuf type extension.

    Inherit this class and define your own `message` method which will convert a given data into the
        `descriptor` type.
    """

    # A message type from the compiled *.proto file.
    descriptor = None

    @classmethod
    @abstractmethod
    def message(cls, *args, **kwargs):
        """Define your own converter into the `descriptor` type. Use it like an Instance->Dict converter"""
        pass

    @classmethod
    def decode(cls, binary):
        assert (
            cls.descriptor is not None
        ), "You must define a descriptor as one from *.proto file"

        return cls.descriptor.FromString(binary)


class ProtobufResponse(Response):
    def __init__(self, message, status):
        super().__init__(
            response=message.SerializeToString(),
            content_type=PROTOBUF_MIMETYPE,
            status=status,
        )


def wrap_proto(protobuf_type: Type[ProtobufType]) -> ProtobufResponse:
    """Creates a compatible HTTP response with the Protobuf type.

    Args:
        protobuf_type (ProtobufType). A descriptor type from the compiled *.proto file.

    Returns:
        An Error or serialized Protobuf message.
    """

    def _wrap_response(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            content, status, error = uapi.resolve_status(f, *args, **kwargs)
            if error:
                message = Error.message(status, error)
            else:
                message = protobuf_type.message(content)

            pb_response = ProtobufResponse(
                message=message,
                status=status,
            )

            return pb_response

        return wrapper

    return _wrap_response


class UserInfoResponse(ProtobufType):
    descriptor = UserInfoResponseProto

    @classmethod
    def message(cls, payload):
        response = UserInfoResponseProto()
        response.user.id = payload["id"]
        response.user.email = payload["email"] or ""
        response.user.login = payload["login"] or ""
        response.user.role = payload["role"] or ""

        return response


class UserInfoRequest(ProtobufType):
    descriptor = UserInfoRequestProto

    @classmethod
    def message(cls, payload):
        return cls.descriptor(id=payload["user_id"])


class Error(ProtobufType):
    descriptor = ErrorProto

    @classmethod
    def message(cls, status: int, error: str):
        return cls.descriptor(status=status, error=error)
