import os

from main import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run_server(host='0.0.0.0', port=port)
