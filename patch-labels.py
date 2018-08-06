
import logging
FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(format=FORMAT,level=logging.DEBUG)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
from pprint import pprint
from kubernetes import client
from eksauth import EksAuth
import boto3
import json

def getEc2Tags(instance):
  k8stags={ "metadata": { "labels": {}}}
  ec2 = boto3.client('ec2',region_name='us-west-2')
  tags=ec2.describe_instances(InstanceIds=[instance])['Reservations'][0]['Instances'][0]['Tags']
  for tag in ec2.describe_instances(InstanceIds=[instance])['Reservations'][0]['Instances'][0]['Tags']:
    if 'label.kubernetes.io/' in tag['Key']:
      print("%s %s" % (tag['Key'], tag['Value']))
      k8stags['metadata']['labels'][tag['Key']] = tag['Value']
  if k8stags['metadata']['labels']:
    #print (k8stags)
    print("K8STags found %s" %(k8stags))
    return k8stags
  else:
    return None

def main():
  from kubernetes import client
  client2 = EksAuth('eks-sample')
  client2.roleArn='arn:aws:iam::237876908982:role/Admin'

  #body = { "metadata": { "labels": { "node-role.kubernetes.io/"+tagname : tagvalue}}}
  try:
    eks = client2.getKubernetesConfig()
    logging.debug('EKS ' + str(eks))
    api = client.ApiClient(eks)
    cli = client.CoreV1Api(api)
    #b=cli.list_pod_for_all_namespaces(limit=1)
    #pprint(cli.list_node())
    for item in cli.list_node().items:
      print("name: %s instance_id: %s" % (item.metadata.name,item.spec.external_id))
      tags=getEc2Tags(item.spec.external_id)
      print(tags)
      if tags is not None:
        print ("Patching node %s" % (item.metadata.name))
        pprint(json.loads(json.dumps(tags)))
        result = cli.patch_node(item.metadata.name, json.loads(json.dumps(tags)))
        pprint(result)
  except Exception as e :
    logging.info(e)

if __name__ == "__main__":
  main()
