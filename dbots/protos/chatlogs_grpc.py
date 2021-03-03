# Generated by the Protocol Buffers compiler. DO NOT EDIT!
# source: chatlogs.proto
# plugin: grpclib.plugin.main
import abc
import typing

import grpclib.const
import grpclib.client
if typing.TYPE_CHECKING:
    import grpclib.server

from . import chatlogs_pb2


class ChatlogsBase(abc.ABC):

    @abc.abstractmethod
    async def Create(self, stream: 'grpclib.server.Stream[chatlogs_pb2.CreateRequest, chatlogs_pb2.CreateReply]') -> None:
        pass

    @abc.abstractmethod
    async def Load(self, stream: 'grpclib.server.Stream[chatlogs_pb2.LoadRequest, chatlogs_pb2.LoadReply]') -> None:
        pass

    def __mapping__(self) -> typing.Dict[str, grpclib.const.Handler]:
        return {
            '/chatlogs.Chatlogs/Create': grpclib.const.Handler(
                self.Create,
                grpclib.const.Cardinality.UNARY_STREAM,
                chatlogs_pb2.CreateRequest,
                chatlogs_pb2.CreateReply,
            ),
            '/chatlogs.Chatlogs/Load': grpclib.const.Handler(
                self.Load,
                grpclib.const.Cardinality.UNARY_STREAM,
                chatlogs_pb2.LoadRequest,
                chatlogs_pb2.LoadReply,
            ),
        }


class ChatlogsStub:

    def __init__(self, channel: grpclib.client.Channel) -> None:
        self.Create = grpclib.client.UnaryStreamMethod(
            channel,
            '/chatlogs.Chatlogs/Create',
            chatlogs_pb2.CreateRequest,
            chatlogs_pb2.CreateReply,
        )
        self.Load = grpclib.client.UnaryStreamMethod(
            channel,
            '/chatlogs.Chatlogs/Load',
            chatlogs_pb2.LoadRequest,
            chatlogs_pb2.LoadReply,
        )
