#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import falcon
from wsgiref.simple_server import make_server
import json
from dynaconf import Dynaconf

# Configuration
settings = Dynaconf(settings_files=["../config/settings.yaml"])
port = settings.get("server.port", 8000)

runPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(runPath, ".."))

from lib.cpeguesser import CPEGuesser


class Search:
    def _is_valid_part(self, part):
        return part in CPEGuesser.VALID_CPE_PARTS

    def _split_query(self, query):
        return [keyword for keyword in query.split() if keyword]

    def _search(self, query, part, resp):
        if not query:
            resp.status = falcon.HTTP_400
            resp.media = "Missing query array or incorrect JSON format"
            return

        if part is not None and not self._is_valid_part(part):
            resp.status = falcon.HTTP_400
            resp.media = "Invalid part parameter. Allowed values are: a, h, o"
            return

        cpeGuesser = CPEGuesser()
        resp.media = cpeGuesser.guessCpe(query, part=part)

    def on_post(self, req, resp):
        data_post = req.bounded_stream.read()
        js = data_post.decode("utf-8")
        try:
            q = json.loads(js)
        except ValueError:
            resp.status = falcon.HTTP_400
            resp.media = "Missing query array or incorrect JSON format"
            return

        if "query" in q:
            pass
        else:
            resp.status = falcon.HTTP_400
            resp.media = "Missing query array or incorrect JSON format"
            return

        part = q.get("part")
        if isinstance(part, str):
            part = part.lower()

        self._search(q["query"], part, resp)

    def on_get(self, req, resp):
        query = req.get_param("q")
        part = req.get_param("part")

        if isinstance(part, str):
            part = part.lower()

        self._search(self._split_query(query or ""), part, resp)


class Unique:
    def on_post(self, req, resp):
        data_post = req.bounded_stream.read()
        js = data_post.decode("utf-8")
        try:
            q = json.loads(js)
        except ValueError:
            resp.status = falcon.HTTP_400
            resp.media = "Missing query array or incorrect JSON format"
            return

        if "query" in q:
            pass
        else:
            resp.status = falcon.HTTP_400
            resp.media = "Missing query array or incorrect JSON format"
            return

        part = q.get("part")
        if isinstance(part, str):
            part = part.lower()
        elif part is not None:
            part = None

        if part is not None and part not in CPEGuesser.VALID_CPE_PARTS:
            resp.status = falcon.HTTP_400
            resp.media = "Invalid part parameter. Allowed values are: a, h, o"
            return

        cpeGuesser = CPEGuesser()
        try:
            r = cpeGuesser.guessCpe(q["query"], part=part)[:1][0][1]
        except:
            r = []
        resp.media = r


if __name__ == "__main__":
    app = falcon.App()
    app.add_route("/search", Search())
    app.add_route("/unique", Unique())

    try:
        with make_server("", port, app) as httpd:
            print(f"Serving on port {port}...")
            httpd.serve_forever()
    except OSError as e:
        print(e)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)
