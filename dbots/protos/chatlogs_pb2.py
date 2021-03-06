# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chatlogs.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='chatlogs.proto',
  package='chatlogs',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0e\x63hatlogs.proto\x12\x08\x63hatlogs\"\xc2\x03\n\x0b\x43hatlogData\x12/\n\x08messages\x18\x01 \x03(\x0b\x32\x1d.chatlogs.ChatlogData.Message\x12/\n\x05users\x18\x02 \x03(\x0b\x32 .chatlogs.ChatlogData.UsersEntry\x1a\xc5\x01\n\x07Message\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\t\x12\x0e\n\x06pinned\x18\x03 \x01(\x08\x12\x11\n\tauthor_id\x18\x04 \x01(\t\x12=\n\x0b\x61ttachments\x18\x05 \x03(\x0b\x32(.chatlogs.ChatlogData.Message.Attachment\x12\x0e\n\x06\x65mbeds\x18\x06 \x03(\x0c\x1a+\n\nAttachment\x12\x10\n\x08\x66ilename\x18\x01 \x01(\t\x12\x0b\n\x03url\x18\x02 \x01(\t\x1a?\n\x04User\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x15\n\rdiscriminator\x18\x03 \x01(\t\x12\x0e\n\x06\x61vatar\x18\x04 \x01(\t\x1aH\n\nUsersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12)\n\x05value\x18\x02 \x01(\x0b\x32\x1a.chatlogs.ChatlogData.User:\x02\x38\x01\"M\n\rCreateRequest\x12\x12\n\nchannel_id\x18\x01 \x01(\t\x12\x15\n\rmessage_count\x18\x02 \x01(\r\x12\x11\n\tbefore_id\x18\x03 \x01(\t\"2\n\x0b\x43reateReply\x12#\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\x15.chatlogs.ChatlogData\"]\n\x0bLoadRequest\x12\x12\n\nchannel_id\x18\x01 \x01(\t\x12#\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x15.chatlogs.ChatlogData\x12\x15\n\rmessage_count\x18\x03 \x01(\r\"\x0b\n\tLoadReply2|\n\x08\x43hatlogs\x12:\n\x06\x43reate\x12\x17.chatlogs.CreateRequest\x1a\x15.chatlogs.CreateReply\"\x00\x12\x34\n\x04Load\x12\x15.chatlogs.LoadRequest\x1a\x13.chatlogs.LoadReply\"\x00\x62\x06proto3'
)




_CHATLOGDATA_MESSAGE_ATTACHMENT = _descriptor.Descriptor(
  name='Attachment',
  full_name='chatlogs.ChatlogData.Message.Attachment',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='filename', full_name='chatlogs.ChatlogData.Message.Attachment.filename', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='url', full_name='chatlogs.ChatlogData.Message.Attachment.url', index=1,
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
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=297,
  serialized_end=340,
)

_CHATLOGDATA_MESSAGE = _descriptor.Descriptor(
  name='Message',
  full_name='chatlogs.ChatlogData.Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='chatlogs.ChatlogData.Message.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='content', full_name='chatlogs.ChatlogData.Message.content', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='pinned', full_name='chatlogs.ChatlogData.Message.pinned', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='author_id', full_name='chatlogs.ChatlogData.Message.author_id', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='attachments', full_name='chatlogs.ChatlogData.Message.attachments', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='embeds', full_name='chatlogs.ChatlogData.Message.embeds', index=5,
      number=6, type=12, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_CHATLOGDATA_MESSAGE_ATTACHMENT, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=143,
  serialized_end=340,
)

_CHATLOGDATA_USER = _descriptor.Descriptor(
  name='User',
  full_name='chatlogs.ChatlogData.User',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='username', full_name='chatlogs.ChatlogData.User.username', index=0,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='discriminator', full_name='chatlogs.ChatlogData.User.discriminator', index=1,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='avatar', full_name='chatlogs.ChatlogData.User.avatar', index=2,
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
  serialized_start=342,
  serialized_end=405,
)

_CHATLOGDATA_USERSENTRY = _descriptor.Descriptor(
  name='UsersEntry',
  full_name='chatlogs.ChatlogData.UsersEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='chatlogs.ChatlogData.UsersEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='chatlogs.ChatlogData.UsersEntry.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
  serialized_start=407,
  serialized_end=479,
)

_CHATLOGDATA = _descriptor.Descriptor(
  name='ChatlogData',
  full_name='chatlogs.ChatlogData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='messages', full_name='chatlogs.ChatlogData.messages', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='users', full_name='chatlogs.ChatlogData.users', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_CHATLOGDATA_MESSAGE, _CHATLOGDATA_USER, _CHATLOGDATA_USERSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=29,
  serialized_end=479,
)


_CREATEREQUEST = _descriptor.Descriptor(
  name='CreateRequest',
  full_name='chatlogs.CreateRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='channel_id', full_name='chatlogs.CreateRequest.channel_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='message_count', full_name='chatlogs.CreateRequest.message_count', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='before_id', full_name='chatlogs.CreateRequest.before_id', index=2,
      number=3, type=9, cpp_type=9, label=1,
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
  serialized_start=481,
  serialized_end=558,
)


_CREATEREPLY = _descriptor.Descriptor(
  name='CreateReply',
  full_name='chatlogs.CreateReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='data', full_name='chatlogs.CreateReply.data', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
  serialized_start=560,
  serialized_end=610,
)


_LOADREQUEST = _descriptor.Descriptor(
  name='LoadRequest',
  full_name='chatlogs.LoadRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='channel_id', full_name='chatlogs.LoadRequest.channel_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data', full_name='chatlogs.LoadRequest.data', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='message_count', full_name='chatlogs.LoadRequest.message_count', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=612,
  serialized_end=705,
)


_LOADREPLY = _descriptor.Descriptor(
  name='LoadReply',
  full_name='chatlogs.LoadReply',
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
  serialized_start=707,
  serialized_end=718,
)

_CHATLOGDATA_MESSAGE_ATTACHMENT.containing_type = _CHATLOGDATA_MESSAGE
_CHATLOGDATA_MESSAGE.fields_by_name['attachments'].message_type = _CHATLOGDATA_MESSAGE_ATTACHMENT
_CHATLOGDATA_MESSAGE.containing_type = _CHATLOGDATA
_CHATLOGDATA_USER.containing_type = _CHATLOGDATA
_CHATLOGDATA_USERSENTRY.fields_by_name['value'].message_type = _CHATLOGDATA_USER
_CHATLOGDATA_USERSENTRY.containing_type = _CHATLOGDATA
_CHATLOGDATA.fields_by_name['messages'].message_type = _CHATLOGDATA_MESSAGE
_CHATLOGDATA.fields_by_name['users'].message_type = _CHATLOGDATA_USERSENTRY
_CREATEREPLY.fields_by_name['data'].message_type = _CHATLOGDATA
_LOADREQUEST.fields_by_name['data'].message_type = _CHATLOGDATA
DESCRIPTOR.message_types_by_name['ChatlogData'] = _CHATLOGDATA
DESCRIPTOR.message_types_by_name['CreateRequest'] = _CREATEREQUEST
DESCRIPTOR.message_types_by_name['CreateReply'] = _CREATEREPLY
DESCRIPTOR.message_types_by_name['LoadRequest'] = _LOADREQUEST
DESCRIPTOR.message_types_by_name['LoadReply'] = _LOADREPLY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ChatlogData = _reflection.GeneratedProtocolMessageType('ChatlogData', (_message.Message,), {

  'Message' : _reflection.GeneratedProtocolMessageType('Message', (_message.Message,), {

    'Attachment' : _reflection.GeneratedProtocolMessageType('Attachment', (_message.Message,), {
      'DESCRIPTOR' : _CHATLOGDATA_MESSAGE_ATTACHMENT,
      '__module__' : 'chatlogs_pb2'
      # @@protoc_insertion_point(class_scope:chatlogs.ChatlogData.Message.Attachment)
      })
    ,
    'DESCRIPTOR' : _CHATLOGDATA_MESSAGE,
    '__module__' : 'chatlogs_pb2'
    # @@protoc_insertion_point(class_scope:chatlogs.ChatlogData.Message)
    })
  ,

  'User' : _reflection.GeneratedProtocolMessageType('User', (_message.Message,), {
    'DESCRIPTOR' : _CHATLOGDATA_USER,
    '__module__' : 'chatlogs_pb2'
    # @@protoc_insertion_point(class_scope:chatlogs.ChatlogData.User)
    })
  ,

  'UsersEntry' : _reflection.GeneratedProtocolMessageType('UsersEntry', (_message.Message,), {
    'DESCRIPTOR' : _CHATLOGDATA_USERSENTRY,
    '__module__' : 'chatlogs_pb2'
    # @@protoc_insertion_point(class_scope:chatlogs.ChatlogData.UsersEntry)
    })
  ,
  'DESCRIPTOR' : _CHATLOGDATA,
  '__module__' : 'chatlogs_pb2'
  # @@protoc_insertion_point(class_scope:chatlogs.ChatlogData)
  })
_sym_db.RegisterMessage(ChatlogData)
_sym_db.RegisterMessage(ChatlogData.Message)
_sym_db.RegisterMessage(ChatlogData.Message.Attachment)
_sym_db.RegisterMessage(ChatlogData.User)
_sym_db.RegisterMessage(ChatlogData.UsersEntry)

CreateRequest = _reflection.GeneratedProtocolMessageType('CreateRequest', (_message.Message,), {
  'DESCRIPTOR' : _CREATEREQUEST,
  '__module__' : 'chatlogs_pb2'
  # @@protoc_insertion_point(class_scope:chatlogs.CreateRequest)
  })
_sym_db.RegisterMessage(CreateRequest)

CreateReply = _reflection.GeneratedProtocolMessageType('CreateReply', (_message.Message,), {
  'DESCRIPTOR' : _CREATEREPLY,
  '__module__' : 'chatlogs_pb2'
  # @@protoc_insertion_point(class_scope:chatlogs.CreateReply)
  })
_sym_db.RegisterMessage(CreateReply)

LoadRequest = _reflection.GeneratedProtocolMessageType('LoadRequest', (_message.Message,), {
  'DESCRIPTOR' : _LOADREQUEST,
  '__module__' : 'chatlogs_pb2'
  # @@protoc_insertion_point(class_scope:chatlogs.LoadRequest)
  })
_sym_db.RegisterMessage(LoadRequest)

LoadReply = _reflection.GeneratedProtocolMessageType('LoadReply', (_message.Message,), {
  'DESCRIPTOR' : _LOADREPLY,
  '__module__' : 'chatlogs_pb2'
  # @@protoc_insertion_point(class_scope:chatlogs.LoadReply)
  })
_sym_db.RegisterMessage(LoadReply)


_CHATLOGDATA_USERSENTRY._options = None

_CHATLOGS = _descriptor.ServiceDescriptor(
  name='Chatlogs',
  full_name='chatlogs.Chatlogs',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=720,
  serialized_end=844,
  methods=[
  _descriptor.MethodDescriptor(
    name='Create',
    full_name='chatlogs.Chatlogs.Create',
    index=0,
    containing_service=None,
    input_type=_CREATEREQUEST,
    output_type=_CREATEREPLY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='Load',
    full_name='chatlogs.Chatlogs.Load',
    index=1,
    containing_service=None,
    input_type=_LOADREQUEST,
    output_type=_LOADREPLY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_CHATLOGS)

DESCRIPTOR.services_by_name['Chatlogs'] = _CHATLOGS

# @@protoc_insertion_point(module_scope)
