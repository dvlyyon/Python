#!/usr/bin/bash
set -euo pipefail

proto_imports=".:/home/dyang/Workspace/pyvenv/g30p310sh/lib/python3.10/site-packages"
proto_dir="nbi/gnmi/v0_7_0/protocol"

#python -m grpc_tools.protoc -I=$proto_imports --python_out=$proto_dir --grpc_python_out=$proto_dir $proto_dir/gnmi.proto
#python -m grpc_tools.protoc -I=$proto_imports --python_out=$proto_dir --grpc_python_out=$proto_dir $proto_dir/gnmi_ext.proto
python -m grpc_tools.protoc -I=$proto_imports --python_out=. --grpc_python_out=. $proto_dir/gnmi.proto
python -m grpc_tools.protoc -I=$proto_imports --python_out=. --grpc_python_out=. $proto_dir/gnmi_ext.proto

