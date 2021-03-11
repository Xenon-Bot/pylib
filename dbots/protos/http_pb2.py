# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: http.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='http.proto',
  package='http',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\nhttp.proto\x12\x04http\"\xd0\x02\n\x0bHTTPRequest\x12\x0c\n\x04path\x18\x01 \x01(\t\x12\x0e\n\x06method\x18\x02 \x01(\t\x12)\n\x04\x61rgs\x18\x03 \x03(\x0b\x32\x1b.http.HTTPRequest.ArgsEntry\x12-\n\x06params\x18\x04 \x03(\x0b\x32\x1d.http.HTTPRequest.ParamsEntry\x12/\n\x07headers\x18\x05 \x03(\x0b\x32\x1e.http.HTTPRequest.HeadersEntry\x12\x0c\n\x04\x62ody\x18\x06 \x01(\x0c\x1a+\n\tArgsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x1a-\n\x0bParamsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x1a.\n\x0cHeadersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\x8e\x01\n\x0cHTTPResponse\x12\x0e\n\x06status\x18\x01 \x01(\r\x12\x30\n\x07headers\x18\x02 \x03(\x0b\x32\x1f.http.HTTPResponse.HeadersEntry\x12\x0c\n\x04\x62ody\x18\x03 \x01(\x0c\x1a.\n\x0cHeadersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"R\n\tRateLimit\x12\r\n\x05total\x18\x01 \x01(\r\x12\x11\n\tremaining\x18\x02 \x01(\r\x12\x13\n\x0breset_after\x18\x03 \x01(\x04\x12\x0e\n\x06\x62ucket\x18\x04 \x01(\t\"\x93\x01\n\x13GetRateLimitRequest\x12\x0c\n\x04path\x18\x01 \x01(\t\x12\x0e\n\x06method\x18\x02 \x01(\t\x12\x31\n\x04\x61rgs\x18\x03 \x03(\x0b\x32#.http.GetRateLimitRequest.ArgsEntry\x1a+\n\tArgsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\x1b\n\x19GetGlobalRateLimitRequest2\xc2\x01\n\x04HTTP\x12\x32\n\x07Request\x12\x11.http.HTTPRequest\x1a\x12.http.HTTPResponse\"\x00\x12<\n\x0cGetRateLimit\x12\x19.http.GetRateLimitRequest\x1a\x0f.http.RateLimit\"\x00\x12H\n\x12GetGlobalRateLimit\x12\x1f.http.GetGlobalRateLimitRequest\x1a\x0f.http.RateLimit\"\x00\x62\x06proto3'
)




_HTTPREQUEST_ARGSENTRY = _descriptor.Descriptor(
  name='ArgsEntry',
  full_name='http.HTTPRequest.ArgsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='http.HTTPRequest.ArgsEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='http.HTTPRequest.ArgsEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=219,
  serialized_end=262,
)

_HTTPREQUEST_PARAMSENTRY = _descriptor.Descriptor(
  name='ParamsEntry',
  full_name='http.HTTPRequest.ParamsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='http.HTTPRequest.ParamsEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='http.HTTPRequest.ParamsEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=264,
  serialized_end=309,
)

_HTTPREQUEST_HEADERSENTRY = _descriptor.Descriptor(
  name='HeadersEntry',
  full_name='http.HTTPRequest.HeadersEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='http.HTTPRequest.HeadersEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='http.HTTPRequest.HeadersEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=311,
  serialized_end=357,
)

_HTTPREQUEST = _descriptor.Descriptor(
  name='HTTPRequest',
  full_name='http.HTTPRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='path', full_name='http.HTTPRequest.path', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='method', full_name='http.HTTPRequest.method', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='args', full_name='http.HTTPRequest.args', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='params', full_name='http.HTTPRequest.params', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='headers', full_name='http.HTTPRequest.headers', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='body', full_name='http.HTTPRequest.body', index=5,
      number=6, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_HTTPREQUEST_ARGSENTRY, _HTTPREQUEST_PARAMSENTRY, _HTTPREQUEST_HEADERSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=21,
  serialized_end=357,
)


_HTTPRESPONSE_HEADERSENTRY = _descriptor.Descriptor(
  name='HeadersEntry',
  full_name='http.HTTPResponse.HeadersEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='http.HTTPResponse.HeadersEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='http.HTTPResponse.HeadersEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=311,
  serialized_end=357,
)

_HTTPRESPONSE = _descriptor.Descriptor(
  name='HTTPResponse',
  full_name='http.HTTPResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='http.HTTPResponse.status', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='headers', full_name='http.HTTPResponse.headers', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='body', full_name='http.HTTPResponse.body', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_HTTPRESPONSE_HEADERSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=360,
  serialized_end=502,
)


_RATELIMIT = _descriptor.Descriptor(
  name='RateLimit',
  full_name='http.RateLimit',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='total', full_name='http.RateLimit.total', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='remaining', full_name='http.RateLimit.remaining', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='reset_after', full_name='http.RateLimit.reset_after', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='bucket', full_name='http.RateLimit.bucket', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=504,
  serialized_end=586,
)


_GETRATELIMITREQUEST_ARGSENTRY = _descriptor.Descriptor(
  name='ArgsEntry',
  full_name='http.GetRateLimitRequest.ArgsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='http.GetRateLimitRequest.ArgsEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='http.GetRateLimitRequest.ArgsEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=219,
  serialized_end=262,
)

_GETRATELIMITREQUEST = _descriptor.Descriptor(
  name='GetRateLimitRequest',
  full_name='http.GetRateLimitRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='path', full_name='http.GetRateLimitRequest.path', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='method', full_name='http.GetRateLimitRequest.method', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='args', full_name='http.GetRateLimitRequest.args', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_GETRATELIMITREQUEST_ARGSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=589,
  serialized_end=736,
)


_GETGLOBALRATELIMITREQUEST = _descriptor.Descriptor(
  name='GetGlobalRateLimitRequest',
  full_name='http.GetGlobalRateLimitRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=738,
  serialized_end=765,
)

_HTTPREQUEST_ARGSENTRY.containing_type = _HTTPREQUEST
_HTTPREQUEST_PARAMSENTRY.containing_type = _HTTPREQUEST
_HTTPREQUEST_HEADERSENTRY.containing_type = _HTTPREQUEST
_HTTPREQUEST.fields_by_name['args'].message_type = _HTTPREQUEST_ARGSENTRY
_HTTPREQUEST.fields_by_name['params'].message_type = _HTTPREQUEST_PARAMSENTRY
_HTTPREQUEST.fields_by_name['headers'].message_type = _HTTPREQUEST_HEADERSENTRY
_HTTPRESPONSE_HEADERSENTRY.containing_type = _HTTPRESPONSE
_HTTPRESPONSE.fields_by_name['headers'].message_type = _HTTPRESPONSE_HEADERSENTRY
_GETRATELIMITREQUEST_ARGSENTRY.containing_type = _GETRATELIMITREQUEST
_GETRATELIMITREQUEST.fields_by_name['args'].message_type = _GETRATELIMITREQUEST_ARGSENTRY
DESCRIPTOR.message_types_by_name['HTTPRequest'] = _HTTPREQUEST
DESCRIPTOR.message_types_by_name['HTTPResponse'] = _HTTPRESPONSE
DESCRIPTOR.message_types_by_name['RateLimit'] = _RATELIMIT
DESCRIPTOR.message_types_by_name['GetRateLimitRequest'] = _GETRATELIMITREQUEST
DESCRIPTOR.message_types_by_name['GetGlobalRateLimitRequest'] = _GETGLOBALRATELIMITREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

HTTPRequest = _reflection.GeneratedProtocolMessageType('HTTPRequest', (_message.Message,), {

  'ArgsEntry' : _reflection.GeneratedProtocolMessageType('ArgsEntry', (_message.Message,), {
    'DESCRIPTOR' : _HTTPREQUEST_ARGSENTRY,
    '__module__' : 'http_pb2'
    # @@protoc_insertion_point(class_scope:http.HTTPRequest.ArgsEntry)
    })
  ,

  'ParamsEntry' : _reflection.GeneratedProtocolMessageType('ParamsEntry', (_message.Message,), {
    'DESCRIPTOR' : _HTTPREQUEST_PARAMSENTRY,
    '__module__' : 'http_pb2'
    # @@protoc_insertion_point(class_scope:http.HTTPRequest.ParamsEntry)
    })
  ,

  'HeadersEntry' : _reflection.GeneratedProtocolMessageType('HeadersEntry', (_message.Message,), {
    'DESCRIPTOR' : _HTTPREQUEST_HEADERSENTRY,
    '__module__' : 'http_pb2'
    # @@protoc_insertion_point(class_scope:http.HTTPRequest.HeadersEntry)
    })
  ,
  'DESCRIPTOR' : _HTTPREQUEST,
  '__module__' : 'http_pb2'
  # @@protoc_insertion_point(class_scope:http.HTTPRequest)
  })
_sym_db.RegisterMessage(HTTPRequest)
_sym_db.RegisterMessage(HTTPRequest.ArgsEntry)
_sym_db.RegisterMessage(HTTPRequest.ParamsEntry)
_sym_db.RegisterMessage(HTTPRequest.HeadersEntry)

HTTPResponse = _reflection.GeneratedProtocolMessageType('HTTPResponse', (_message.Message,), {

  'HeadersEntry' : _reflection.GeneratedProtocolMessageType('HeadersEntry', (_message.Message,), {
    'DESCRIPTOR' : _HTTPRESPONSE_HEADERSENTRY,
    '__module__' : 'http_pb2'
    # @@protoc_insertion_point(class_scope:http.HTTPResponse.HeadersEntry)
    })
  ,
  'DESCRIPTOR' : _HTTPRESPONSE,
  '__module__' : 'http_pb2'
  # @@protoc_insertion_point(class_scope:http.HTTPResponse)
  })
_sym_db.RegisterMessage(HTTPResponse)
_sym_db.RegisterMessage(HTTPResponse.HeadersEntry)

RateLimit = _reflection.GeneratedProtocolMessageType('RateLimit', (_message.Message,), {
  'DESCRIPTOR' : _RATELIMIT,
  '__module__' : 'http_pb2'
  # @@protoc_insertion_point(class_scope:http.RateLimit)
  })
_sym_db.RegisterMessage(RateLimit)

GetRateLimitRequest = _reflection.GeneratedProtocolMessageType('GetRateLimitRequest', (_message.Message,), {

  'ArgsEntry' : _reflection.GeneratedProtocolMessageType('ArgsEntry', (_message.Message,), {
    'DESCRIPTOR' : _GETRATELIMITREQUEST_ARGSENTRY,
    '__module__' : 'http_pb2'
    # @@protoc_insertion_point(class_scope:http.GetRateLimitRequest.ArgsEntry)
    })
  ,
  'DESCRIPTOR' : _GETRATELIMITREQUEST,
  '__module__' : 'http_pb2'
  # @@protoc_insertion_point(class_scope:http.GetRateLimitRequest)
  })
_sym_db.RegisterMessage(GetRateLimitRequest)
_sym_db.RegisterMessage(GetRateLimitRequest.ArgsEntry)

GetGlobalRateLimitRequest = _reflection.GeneratedProtocolMessageType('GetGlobalRateLimitRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETGLOBALRATELIMITREQUEST,
  '__module__' : 'http_pb2'
  # @@protoc_insertion_point(class_scope:http.GetGlobalRateLimitRequest)
  })
_sym_db.RegisterMessage(GetGlobalRateLimitRequest)


_HTTPREQUEST_ARGSENTRY._options = None
_HTTPREQUEST_PARAMSENTRY._options = None
_HTTPREQUEST_HEADERSENTRY._options = None
_HTTPRESPONSE_HEADERSENTRY._options = None
_GETRATELIMITREQUEST_ARGSENTRY._options = None

_HTTP = _descriptor.ServiceDescriptor(
  name='HTTP',
  full_name='http.HTTP',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=768,
  serialized_end=962,
  methods=[
  _descriptor.MethodDescriptor(
    name='Request',
    full_name='http.HTTP.Request',
    index=0,
    containing_service=None,
    input_type=_HTTPREQUEST,
    output_type=_HTTPRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='GetRateLimit',
    full_name='http.HTTP.GetRateLimit',
    index=1,
    containing_service=None,
    input_type=_GETRATELIMITREQUEST,
    output_type=_RATELIMIT,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='GetGlobalRateLimit',
    full_name='http.HTTP.GetGlobalRateLimit',
    index=2,
    containing_service=None,
    input_type=_GETGLOBALRATELIMITREQUEST,
    output_type=_RATELIMIT,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_HTTP)

DESCRIPTOR.services_by_name['HTTP'] = _HTTP

# @@protoc_insertion_point(module_scope)
