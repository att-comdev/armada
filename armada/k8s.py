from kubernetes import client, config

class K8s(object):
    '''
    Object to obtain the local kube config file
    '''
    def __init__(self):
        '''
        Initialize connection to Kubernetes
        '''
        config.load_kube_config()
        self.client = client.CoreV1Api()
