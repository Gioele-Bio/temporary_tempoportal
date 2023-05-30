from dash_app import create_dash_application

# Run App
if __name__ == '__main__':
    app = create_dash_application(__name__, local=True)

    server = app.server

    app.run_server(port=9000, debug=True) 
