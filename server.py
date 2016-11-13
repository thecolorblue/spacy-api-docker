#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_restful import Api

from api.parse import Parse
# from api.query import Query

app = Flask("spaCy API")
api = Api(app)

api.add_resource(Parse, '/parse')
# api.add_resource(Query, '/query')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.environ.get('PORT') or 5000)
