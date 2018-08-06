
import logging
FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(format=FORMAT,level=logging.INFO)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
from pprint import pprint
from kubernetes import client
from eksauth import EksAuth


def main():
  from kubernetes import client
  client2 = EksAuth('eks-sample')
  #client2.roleArn='arn:aws:iam::XXXXXXXXXXXXXX:role/KubernetesAdmin'

  body = { "metadata": { "labels": { "nodegroup":None}}}
  try:
    eks = client2.getKubernetesConfig()
    logging.debug('EKS ' + str(eks))
    api = client.ApiClient(eks)
    cli = client.CoreV1Api(api)
    #b=cli.list_pod_for_all_namespaces(limit=1)
    pprint(cli.list_node())
    for item in cli.list_node().items:
      print("name: %s instance_id: %s" % (item.metadata.name,item.spec.external_id))
      cli.patch_node(item.metadata.name, body)
  except Exception as e :
    logging.info(e)

if __name__ == "__main__":
  main()
