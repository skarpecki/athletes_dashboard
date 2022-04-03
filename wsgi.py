from app import create_app, config

if __name__ == "__main__":
    app = create_app()
    app.run(debug=config["APP"]["DEBUG"], 
            host=config["APP"]["REST_HOST"],
            port=config["APP"]["PORT"])