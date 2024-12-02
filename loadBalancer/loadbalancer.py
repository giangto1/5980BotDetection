from flask import Flask, request, jsonify
import requests
import redis
import time
import threading
# from kubernetes import client, config
import redis

cache = redis.Redis(host='localhost', port=6379)
app = Flask(__name__)

# figure out how to find pods :((
pods = [
    "http://pod1:5000",
    "http://pod2:5000",
    "http://pod3:5000"
]

# load kubernetes
# config.load_kube_config()
# v1 = client.AppsV1Api()

# scaling constants
MAX_REQUESTS_PER_SECOND = 10
MIN_REQUESTS_PER_SECOND = 2
CURRENT_REPLICAS = 2 # starting replicas
DEPLOYMENT_NAME = "python-app-deployment"
NAMESPACE = "default"

requestCount = 0
totalRequestCount = 0
lock = threading.Lock()


def scale():
    global CURRENT_REPLICAS
    global requestCount
    while True:
        time.sleep(10)
        with lock:
            throughput = requestCount / 10
            print(f"Number of requests in the last 10 seconds: {requestCount}")
            print(f"Throughput: {throughput} req/s")
            print(f"Latency: {1 / throughput if throughput > 0 else 'N/A'} seconds")
            
            # Check if scaling is needed
            if throughput > MAX_REQUESTS_PER_SECOND and CURRENT_REPLICAS < 5:
                print("Scaling up...")
                CURRENT_REPLICAS += 1
                scale_deployment(CURRENT_REPLICAS)
            elif throughput < MIN_REQUESTS_PER_SECOND and CURRENT_REPLICAS > 1:
                print("Scaling down...")
                CURRENT_REPLICAS -= 1
                scale_deployment(CURRENT_REPLICAS)

            # reset to retrack
            requestCount = 0

def scale_deployment(replicas):
    """Function to scale the Kubernetes deployment."""
    body = {
        'spec': {
            'replicas': replicas
        }
    }
    # response = v1.patch_namespaced_deployment_scale(
    #     name=DEPLOYMENT_NAME, 
    #     namespace=NAMESPACE, 
    #     body=body
    # )
    print(f"Deployment scaled to {replicas} replicas.")


@app.before_request
def new_request():
    global requestCount
    global totalRequestCount
    with lock:
        requestCount += 1
        totalRequestCount += 1

# roundrobin
current_pod = 0

def get_next_pod():
    global current_pod
    pod = pods[current_pod]
    current_pod = (current_pod + 1) % len(pods)
    return pod

@app.route('/load/<user>', methods=['GET'])
def load_balancer(user):

    cached_response = cache.get(user)
    if cached_response:
        return cached_response, 200

    # forward
    pod = get_next_pod()
    pod_response = requests.get(f"{pod}/data")

    # set cache
    cache.set(user, pod_response.text)

    return pod_response.text, pod_response.status_code

if __name__ == '__main__':
    logging_thread = threading.Thread(target=scale)
    logging_thread.daemon = True
    logging_thread.start()
    app.run(host='0.0.0.0', port=5000)
