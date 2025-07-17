import os
from uuid import uuid4

from diagrams import Cluster, Diagram
from diagrams.aws.compute import EC2, Lambda, ECS, EKS
from diagrams.aws.database import DynamodbTable
from diagrams.aws.database import RDS, Aurora, Redshift, Elasticache
from diagrams.aws.network import ALB, APIGateway, CloudFront
from diagrams.aws.integration import SQS, SNS, StepFunctions
from diagrams.aws.storage import S3
from diagrams.aws.security import IAM
from diagrams.aws.management import Cloudwatch

node_types = {
    "EC2": EC2,
    "ALB": ALB,
    "APIGateway": APIGateway,
    "SQS": SQS,
    "RDS": RDS,
    "DynamoDB": DynamodbTable,
    "S3": S3,
    "Lambda": Lambda,
    "SNS": SNS,
    "CloudFront": CloudFront,
    "CloudWatch": Cloudwatch,
    "StepFunctions": StepFunctions,
    "IAM": IAM,
    "ElasticCache": Elasticache,
    "Redshift": Redshift,
    "Aurora": Aurora,
    "ECS": ECS,
    "EKS": EKS,
}

STATIC_DIR = "static"
DIAGRAM_NAME = "diagram"
DIAGRAM_PATH = os.path.join(STATIC_DIR, DIAGRAM_NAME)
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")

def build_diagram(diagram_data: dict) -> str:
    os.makedirs(STATIC_DIR, exist_ok=True)
    if os.path.exists(DIAGRAM_PATH):
        os.remove(DIAGRAM_PATH)

    nodes = {}
    grouped_nodes = {}
    ungrouped_nodes = []

    for node in diagram_data["nodes"]:
        group = node.get("group")
        if group:
            grouped_nodes.setdefault(group, []).append(node)
        else:
            ungrouped_nodes.append(node)

    with Diagram(
            "Generated Diagram",
            show=False,
            outformat="png",
            filename=DIAGRAM_PATH
    ):
        for group_name, group_nodes in grouped_nodes.items():
            with Cluster(group_name):
                for node in group_nodes:
                    NodeClass = node_types.get(node["type"])
                    label = node.get("label", node["id"])
                    if NodeClass:
                        nodes[node["id"]] = NodeClass(label)

        for node in ungrouped_nodes:
            NodeClass = node_types.get(node["type"])
            label = node.get("label", node["id"])
            if NodeClass:
                nodes[node["id"]] = NodeClass(label)

        for edge in diagram_data.get("edges", []):
            src = nodes.get(edge["from"])
            dst = nodes.get(edge["to"])
            if src and dst:
                src >> dst

    return f"{BASE_URL}/static/{DIAGRAM_NAME}.png?{uuid4().hex}" # for skip browser cache