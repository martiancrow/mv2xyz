#!/Users/xiaolongliu/miniconda3/bin/python
# -*- coding:utf8 -*-

import os
from app import create_app, db
from app.models.ua_models import ua_user, ua_session, ua_session_data
from app.models.res_models import res_post, res_file
from flask_migrate import Migrate, MigrateCommand

app = create_app('production')
migrate = Migrate(app, db)

import logging
from logging.handlers import TimedRotatingFileHandler

handler = logging.FileHandler('logs/flask2.log', encoding='UTF-8')
handler.setLevel(logging.DEBUG)
logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
handler.setFormatter(logging_format)
app.logger.addHandler(handler)

if __name__ == "__main__":
	app.run(debug=True)