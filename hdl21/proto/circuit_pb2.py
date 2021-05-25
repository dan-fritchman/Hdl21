# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: circuit.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='circuit.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\rcircuit.proto\"1\n\x07Package\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x18\n\x07modules\x18\x02 \x03(\x0b\x32\x07.Module\"-\n\rQualifiedName\x12\x0e\n\x06\x64omain\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\"/\n\tReference\x12\x1c\n\x02qn\x18\x01 \x01(\x0b\x32\x0e.QualifiedNameH\x00\x42\x04\n\x02to\"K\n\tParameter\x12\x11\n\x07integer\x18\x02 \x01(\x03H\x00\x12\x10\n\x06\x64ouble\x18\x03 \x01(\x01H\x00\x12\x10\n\x06string\x18\x04 \x01(\tH\x00\x42\x07\n\x05value\"|\n\x04Port\x12\x17\n\x06signal\x18\x01 \x01(\x0b\x32\x07.Signal\x12\"\n\tdirection\x18\x02 \x01(\x0e\x32\x0f.Port.Direction\"7\n\tDirection\x12\t\n\x05INPUT\x10\x00\x12\n\n\x06OUTPUT\x10\x01\x12\t\n\x05INOUT\x10\x02\x12\x08\n\x04NONE\x10\x03\"%\n\x06Signal\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\r\n\x05width\x18\x02 \x01(\x03\"1\n\x05Slice\x12\x0e\n\x06signal\x18\x01 \x01(\t\x12\x0b\n\x03top\x18\x02 \x01(\x03\x12\x0b\n\x03\x62ot\x18\x03 \x01(\x03\"$\n\x06\x43oncat\x12\x1a\n\x05parts\x18\x01 \x03(\x0b\x32\x0b.Connection\"a\n\nConnection\x12\x16\n\x03sig\x18\x01 \x01(\x0b\x32\x07.SignalH\x00\x12\x17\n\x05slice\x18\x02 \x01(\x0b\x32\x06.SliceH\x00\x12\x19\n\x06\x63oncat\x18\x03 \x01(\x0b\x32\x07.ConcatH\x00\x42\x07\n\x05stype\"\x94\x02\n\x08Instance\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x1a\n\x06module\x18\x02 \x01(\x0b\x32\n.Reference\x12-\n\nparameters\x18\x03 \x03(\x0b\x32\x19.Instance.ParametersEntry\x12/\n\x0b\x63onnections\x18\x04 \x03(\x0b\x32\x1a.Instance.ConnectionsEntry\x1a=\n\x0fParametersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x19\n\x05value\x18\x02 \x01(\x0b\x32\n.Parameter:\x02\x38\x01\x1a?\n\x10\x43onnectionsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x1a\n\x05value\x18\x02 \x01(\x0b\x32\x0b.Connection:\x02\x38\x01\"\xf6\x01\n\x06Module\x12\x1c\n\x04name\x18\x01 \x01(\x0b\x32\x0e.QualifiedName\x12\x14\n\x05ports\x18\x02 \x03(\x0b\x32\x05.Port\x12\x18\n\x07signals\x18\x03 \x03(\x0b\x32\x07.Signal\x12\x1c\n\tinstances\x18\x04 \x03(\x0b\x32\t.Instance\x12:\n\x12\x64\x65\x66\x61ult_parameters\x18\x05 \x03(\x0b\x32\x1e.Module.DefaultParametersEntry\x1a\x44\n\x16\x44\x65\x66\x61ultParametersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x19\n\x05value\x18\x02 \x01(\x0b\x32\n.Parameter:\x02\x38\x01\x62\x06proto3'
)



_PORT_DIRECTION = _descriptor.EnumDescriptor(
  name='Direction',
  full_name='Port.Direction',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='INPUT', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='OUTPUT', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='INOUT', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='NONE', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=310,
  serialized_end=365,
)
_sym_db.RegisterEnumDescriptor(_PORT_DIRECTION)


_PACKAGE = _descriptor.Descriptor(
  name='Package',
  full_name='Package',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='Package.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='modules', full_name='Package.modules', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=17,
  serialized_end=66,
)


_QUALIFIEDNAME = _descriptor.Descriptor(
  name='QualifiedName',
  full_name='QualifiedName',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='domain', full_name='QualifiedName.domain', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='name', full_name='QualifiedName.name', index=1,
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
  serialized_start=68,
  serialized_end=113,
)


_REFERENCE = _descriptor.Descriptor(
  name='Reference',
  full_name='Reference',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='qn', full_name='Reference.qn', index=0,
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
    _descriptor.OneofDescriptor(
      name='to', full_name='Reference.to',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=115,
  serialized_end=162,
)


_PARAMETER = _descriptor.Descriptor(
  name='Parameter',
  full_name='Parameter',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='integer', full_name='Parameter.integer', index=0,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='double', full_name='Parameter.double', index=1,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='string', full_name='Parameter.string', index=2,
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
    _descriptor.OneofDescriptor(
      name='value', full_name='Parameter.value',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=164,
  serialized_end=239,
)


_PORT = _descriptor.Descriptor(
  name='Port',
  full_name='Port',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='signal', full_name='Port.signal', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='direction', full_name='Port.direction', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _PORT_DIRECTION,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=241,
  serialized_end=365,
)


_SIGNAL = _descriptor.Descriptor(
  name='Signal',
  full_name='Signal',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='Signal.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='width', full_name='Signal.width', index=1,
      number=2, type=3, cpp_type=2, label=1,
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
  serialized_start=367,
  serialized_end=404,
)


_SLICE = _descriptor.Descriptor(
  name='Slice',
  full_name='Slice',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='signal', full_name='Slice.signal', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='top', full_name='Slice.top', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='bot', full_name='Slice.bot', index=2,
      number=3, type=3, cpp_type=2, label=1,
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
  serialized_start=406,
  serialized_end=455,
)


_CONCAT = _descriptor.Descriptor(
  name='Concat',
  full_name='Concat',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='parts', full_name='Concat.parts', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=457,
  serialized_end=493,
)


_CONNECTION = _descriptor.Descriptor(
  name='Connection',
  full_name='Connection',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='sig', full_name='Connection.sig', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='slice', full_name='Connection.slice', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='concat', full_name='Connection.concat', index=2,
      number=3, type=11, cpp_type=10, label=1,
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
    _descriptor.OneofDescriptor(
      name='stype', full_name='Connection.stype',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=495,
  serialized_end=592,
)


_INSTANCE_PARAMETERSENTRY = _descriptor.Descriptor(
  name='ParametersEntry',
  full_name='Instance.ParametersEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='Instance.ParametersEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='Instance.ParametersEntry.value', index=1,
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
  serialized_start=745,
  serialized_end=806,
)

_INSTANCE_CONNECTIONSENTRY = _descriptor.Descriptor(
  name='ConnectionsEntry',
  full_name='Instance.ConnectionsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='Instance.ConnectionsEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='Instance.ConnectionsEntry.value', index=1,
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
  serialized_start=808,
  serialized_end=871,
)

_INSTANCE = _descriptor.Descriptor(
  name='Instance',
  full_name='Instance',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='Instance.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='module', full_name='Instance.module', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='parameters', full_name='Instance.parameters', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='connections', full_name='Instance.connections', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_INSTANCE_PARAMETERSENTRY, _INSTANCE_CONNECTIONSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=595,
  serialized_end=871,
)


_MODULE_DEFAULTPARAMETERSENTRY = _descriptor.Descriptor(
  name='DefaultParametersEntry',
  full_name='Module.DefaultParametersEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='Module.DefaultParametersEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='Module.DefaultParametersEntry.value', index=1,
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
  serialized_start=1052,
  serialized_end=1120,
)

_MODULE = _descriptor.Descriptor(
  name='Module',
  full_name='Module',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='Module.name', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='ports', full_name='Module.ports', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='signals', full_name='Module.signals', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='instances', full_name='Module.instances', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='default_parameters', full_name='Module.default_parameters', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_MODULE_DEFAULTPARAMETERSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=874,
  serialized_end=1120,
)

_PACKAGE.fields_by_name['modules'].message_type = _MODULE
_REFERENCE.fields_by_name['qn'].message_type = _QUALIFIEDNAME
_REFERENCE.oneofs_by_name['to'].fields.append(
  _REFERENCE.fields_by_name['qn'])
_REFERENCE.fields_by_name['qn'].containing_oneof = _REFERENCE.oneofs_by_name['to']
_PARAMETER.oneofs_by_name['value'].fields.append(
  _PARAMETER.fields_by_name['integer'])
_PARAMETER.fields_by_name['integer'].containing_oneof = _PARAMETER.oneofs_by_name['value']
_PARAMETER.oneofs_by_name['value'].fields.append(
  _PARAMETER.fields_by_name['double'])
_PARAMETER.fields_by_name['double'].containing_oneof = _PARAMETER.oneofs_by_name['value']
_PARAMETER.oneofs_by_name['value'].fields.append(
  _PARAMETER.fields_by_name['string'])
_PARAMETER.fields_by_name['string'].containing_oneof = _PARAMETER.oneofs_by_name['value']
_PORT.fields_by_name['signal'].message_type = _SIGNAL
_PORT.fields_by_name['direction'].enum_type = _PORT_DIRECTION
_PORT_DIRECTION.containing_type = _PORT
_CONCAT.fields_by_name['parts'].message_type = _CONNECTION
_CONNECTION.fields_by_name['sig'].message_type = _SIGNAL
_CONNECTION.fields_by_name['slice'].message_type = _SLICE
_CONNECTION.fields_by_name['concat'].message_type = _CONCAT
_CONNECTION.oneofs_by_name['stype'].fields.append(
  _CONNECTION.fields_by_name['sig'])
_CONNECTION.fields_by_name['sig'].containing_oneof = _CONNECTION.oneofs_by_name['stype']
_CONNECTION.oneofs_by_name['stype'].fields.append(
  _CONNECTION.fields_by_name['slice'])
_CONNECTION.fields_by_name['slice'].containing_oneof = _CONNECTION.oneofs_by_name['stype']
_CONNECTION.oneofs_by_name['stype'].fields.append(
  _CONNECTION.fields_by_name['concat'])
_CONNECTION.fields_by_name['concat'].containing_oneof = _CONNECTION.oneofs_by_name['stype']
_INSTANCE_PARAMETERSENTRY.fields_by_name['value'].message_type = _PARAMETER
_INSTANCE_PARAMETERSENTRY.containing_type = _INSTANCE
_INSTANCE_CONNECTIONSENTRY.fields_by_name['value'].message_type = _CONNECTION
_INSTANCE_CONNECTIONSENTRY.containing_type = _INSTANCE
_INSTANCE.fields_by_name['module'].message_type = _REFERENCE
_INSTANCE.fields_by_name['parameters'].message_type = _INSTANCE_PARAMETERSENTRY
_INSTANCE.fields_by_name['connections'].message_type = _INSTANCE_CONNECTIONSENTRY
_MODULE_DEFAULTPARAMETERSENTRY.fields_by_name['value'].message_type = _PARAMETER
_MODULE_DEFAULTPARAMETERSENTRY.containing_type = _MODULE
_MODULE.fields_by_name['name'].message_type = _QUALIFIEDNAME
_MODULE.fields_by_name['ports'].message_type = _PORT
_MODULE.fields_by_name['signals'].message_type = _SIGNAL
_MODULE.fields_by_name['instances'].message_type = _INSTANCE
_MODULE.fields_by_name['default_parameters'].message_type = _MODULE_DEFAULTPARAMETERSENTRY
DESCRIPTOR.message_types_by_name['Package'] = _PACKAGE
DESCRIPTOR.message_types_by_name['QualifiedName'] = _QUALIFIEDNAME
DESCRIPTOR.message_types_by_name['Reference'] = _REFERENCE
DESCRIPTOR.message_types_by_name['Parameter'] = _PARAMETER
DESCRIPTOR.message_types_by_name['Port'] = _PORT
DESCRIPTOR.message_types_by_name['Signal'] = _SIGNAL
DESCRIPTOR.message_types_by_name['Slice'] = _SLICE
DESCRIPTOR.message_types_by_name['Concat'] = _CONCAT
DESCRIPTOR.message_types_by_name['Connection'] = _CONNECTION
DESCRIPTOR.message_types_by_name['Instance'] = _INSTANCE
DESCRIPTOR.message_types_by_name['Module'] = _MODULE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Package = _reflection.GeneratedProtocolMessageType('Package', (_message.Message,), {
  'DESCRIPTOR' : _PACKAGE,
  '__module__' : 'circuit_pb2'
  # @@protoc_insertion_point(class_scope:Package)
  })
_sym_db.RegisterMessage(Package)

QualifiedName = _reflection.GeneratedProtocolMessageType('QualifiedName', (_message.Message,), {
  'DESCRIPTOR' : _QUALIFIEDNAME,
  '__module__' : 'circuit_pb2'
  # @@protoc_insertion_point(class_scope:QualifiedName)
  })
_sym_db.RegisterMessage(QualifiedName)

Reference = _reflection.GeneratedProtocolMessageType('Reference', (_message.Message,), {
  'DESCRIPTOR' : _REFERENCE,
  '__module__' : 'circuit_pb2'
  # @@protoc_insertion_point(class_scope:Reference)
  })
_sym_db.RegisterMessage(Reference)

Parameter = _reflection.GeneratedProtocolMessageType('Parameter', (_message.Message,), {
  'DESCRIPTOR' : _PARAMETER,
  '__module__' : 'circuit_pb2'
  # @@protoc_insertion_point(class_scope:Parameter)
  })
_sym_db.RegisterMessage(Parameter)

Port = _reflection.GeneratedProtocolMessageType('Port', (_message.Message,), {
  'DESCRIPTOR' : _PORT,
  '__module__' : 'circuit_pb2'
  # @@protoc_insertion_point(class_scope:Port)
  })
_sym_db.RegisterMessage(Port)

Signal = _reflection.GeneratedProtocolMessageType('Signal', (_message.Message,), {
  'DESCRIPTOR' : _SIGNAL,
  '__module__' : 'circuit_pb2'
  # @@protoc_insertion_point(class_scope:Signal)
  })
_sym_db.RegisterMessage(Signal)

Slice = _reflection.GeneratedProtocolMessageType('Slice', (_message.Message,), {
  'DESCRIPTOR' : _SLICE,
  '__module__' : 'circuit_pb2'
  # @@protoc_insertion_point(class_scope:Slice)
  })
_sym_db.RegisterMessage(Slice)

Concat = _reflection.GeneratedProtocolMessageType('Concat', (_message.Message,), {
  'DESCRIPTOR' : _CONCAT,
  '__module__' : 'circuit_pb2'
  # @@protoc_insertion_point(class_scope:Concat)
  })
_sym_db.RegisterMessage(Concat)

Connection = _reflection.GeneratedProtocolMessageType('Connection', (_message.Message,), {
  'DESCRIPTOR' : _CONNECTION,
  '__module__' : 'circuit_pb2'
  # @@protoc_insertion_point(class_scope:Connection)
  })
_sym_db.RegisterMessage(Connection)

Instance = _reflection.GeneratedProtocolMessageType('Instance', (_message.Message,), {

  'ParametersEntry' : _reflection.GeneratedProtocolMessageType('ParametersEntry', (_message.Message,), {
    'DESCRIPTOR' : _INSTANCE_PARAMETERSENTRY,
    '__module__' : 'circuit_pb2'
    # @@protoc_insertion_point(class_scope:Instance.ParametersEntry)
    })
  ,

  'ConnectionsEntry' : _reflection.GeneratedProtocolMessageType('ConnectionsEntry', (_message.Message,), {
    'DESCRIPTOR' : _INSTANCE_CONNECTIONSENTRY,
    '__module__' : 'circuit_pb2'
    # @@protoc_insertion_point(class_scope:Instance.ConnectionsEntry)
    })
  ,
  'DESCRIPTOR' : _INSTANCE,
  '__module__' : 'circuit_pb2'
  # @@protoc_insertion_point(class_scope:Instance)
  })
_sym_db.RegisterMessage(Instance)
_sym_db.RegisterMessage(Instance.ParametersEntry)
_sym_db.RegisterMessage(Instance.ConnectionsEntry)

Module = _reflection.GeneratedProtocolMessageType('Module', (_message.Message,), {

  'DefaultParametersEntry' : _reflection.GeneratedProtocolMessageType('DefaultParametersEntry', (_message.Message,), {
    'DESCRIPTOR' : _MODULE_DEFAULTPARAMETERSENTRY,
    '__module__' : 'circuit_pb2'
    # @@protoc_insertion_point(class_scope:Module.DefaultParametersEntry)
    })
  ,
  'DESCRIPTOR' : _MODULE,
  '__module__' : 'circuit_pb2'
  # @@protoc_insertion_point(class_scope:Module)
  })
_sym_db.RegisterMessage(Module)
_sym_db.RegisterMessage(Module.DefaultParametersEntry)


_INSTANCE_PARAMETERSENTRY._options = None
_INSTANCE_CONNECTIONSENTRY._options = None
_MODULE_DEFAULTPARAMETERSENTRY._options = None
# @@protoc_insertion_point(module_scope)