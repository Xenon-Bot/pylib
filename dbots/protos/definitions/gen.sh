pushd $(dirname "$0")

mkdir temp && pushd ./temp

git clone https://github.com/dc-kitebot/isolator

mkdir -p ../../isolator
python3 -m grpc_tools.protoc -I=./isolator/protobuf --python_out=../../isolator --grpclib_python_out=../../isolator ./isolator/protobuf/*.proto
python3 -m grpc_tools.protoc -I=./isolator/protobuf --python_out=../../isolator --grpc_python_out=../../isolator ./isolator/protobuf/*.proto

popd && rm -rf ./temp

python3 -m grpc_tools.protoc -I=. --python_out=../ --grpclib_python_out=../ ./*.proto
python3 -m grpc_tools.protoc -I=. --python_out=../ --grpc_python_out=../ ./*.proto

popd