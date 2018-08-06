#import logging
#FORMAT = "%(asctime)-15s %(message)s"
#logging.basicConfig(format=FORMAT,level=logging.INFO)
#logging.getLogger('boto3').setLevel(logging.CRITICAL)
#logging.getLogger('botocore').setLevel(logging.CRITICAL)
#logging.getLogger('nose').setLevel(logging.CRITICAL)
#logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
from eksauth import EksAuth
from pprint import pprint

def main():
  from kubernetes import client
  client2 = EksAuth('authenticator.albvzzqogi.k8s.local')
  client2.roleArn='arn:aws:iam::297286928529:role/KubernetesAdmin'
  #client2 = EksAuth('eks-sample')

  try:
    eks = client2.getKubernetesConfig()
    api = client.ApiClient(eks)
    cli = client.CoreV1Api(api)
    for item in cli.list_node().items:
      print("name: %s instance_id: %s" % (item.metadata.name.ljust(45),item.spec.external_id))
  except Exception as e :
    logging.info(e)

if __name__ == "__main__":
  main()
