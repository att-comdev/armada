
import falcon
import json
from falcon import HTTP_200

from armada.tiller import Tiller as tillerHandler
from armada.armada import Armada as armadaHandler
from armada.logutil import setup_logging

class Tiller(object):
    '''
    tiller service endpoints
    '''

    def on_get(self, req, resp):
        '''
        get tiller status
        '''
        message = "Tiller Server is {}"
        if tillerHandler().tiller_status():
            resp.data = json.dumps({'message': message.format('Active')})
        else:
            resp.data = json.dumps({'message': message.format('Not Present')})

        resp.content_type = 'application/json'
        resp.status = HTTP_200

class Armada(object):
    '''
    apply armada endpoint service
    '''

    def on_post(self, req, resp):
        armada = armadaHandler(req.stream.read())
        print armada.tiller.k8s.get_namespace_pod()
        armada.sync()

        resp.data = json.dumps({'message': 'Success'})
        resp.content_type = 'application/json'
        resp.status = HTTP_200


wsgi_app = api = falcon.API()

# Routing

url_routes = (
    ('/tiller/status', Tiller()),
    ('/apply', Armada()),
)

for route, service in url_routes:
    api.add_route(route, service)


setup_logging(False)
