# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import chatlogs_pb2 as chatlogs__pb2


class ChatlogsStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Create = channel.unary_stream(
                '/chatlogs.Chatlogs/Create',
                request_serializer=chatlogs__pb2.CreateRequest.SerializeToString,
                response_deserializer=chatlogs__pb2.CreateReply.FromString,
                )
        self.Load = channel.unary_stream(
                '/chatlogs.Chatlogs/Load',
                request_serializer=chatlogs__pb2.LoadRequest.SerializeToString,
                response_deserializer=chatlogs__pb2.LoadReply.FromString,
                )


class ChatlogsServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Create(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Load(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatlogsServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_stream_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=chatlogs__pb2.CreateRequest.FromString,
                    response_serializer=chatlogs__pb2.CreateReply.SerializeToString,
            ),
            'Load': grpc.unary_stream_rpc_method_handler(
                    servicer.Load,
                    request_deserializer=chatlogs__pb2.LoadRequest.FromString,
                    response_serializer=chatlogs__pb2.LoadReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'chatlogs.Chatlogs', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Chatlogs(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Create(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/chatlogs.Chatlogs/Create',
            chatlogs__pb2.CreateRequest.SerializeToString,
            chatlogs__pb2.CreateReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Load(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/chatlogs.Chatlogs/Load',
            chatlogs__pb2.LoadRequest.SerializeToString,
            chatlogs__pb2.LoadReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
