from RPC import create_app

rpc = create_app()
job_processor = rpc.job_processor
