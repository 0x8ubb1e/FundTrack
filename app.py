import logging
from flask import Flask

from routes import init_routes

app = Flask(__name__, static_folder='static', template_folder='templates')

app.logger.setLevel(logging.INFO)

# 初始化路由
init_routes(app)

if __name__ == '__main__':
	app.logger.info("running………………")
	app.run(debug=True, port=22895)
