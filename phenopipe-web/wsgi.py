from server import create_app

app = create_app(configname="production_config", app_name="phenobox-server")
#if __name__ == "__main__":
#    create_app(configname="production_config", app_name="phenobox-server").run()
