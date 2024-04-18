import os

from main import server

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server.run(host='0.0.0.0', port=port)
