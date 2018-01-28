from grpc_tools import protoc

protoc.main(
    (
        '',
        '-I./proto',
        '--python_out=./gen',
        '--grpc_python_out=./gen',
        'proto/phenopipe.proto',
        'proto/phenopipe_iap.proto',
        'proto/phenopipe_r.proto'
    )
)
