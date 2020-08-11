# -*- encoding: utf-8 -*-
# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab

import os

from aws_cdk import (
  core,
  aws_ec2,
  aws_s3 as s3,
  aws_neptune
)


class NeptuneTutorialStack(core.Stack):

  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    # The code that defines your stack goes here
    vpc = aws_ec2.Vpc(self, "NeptuneTutorialVPC",
      max_azs=2,
#      subnet_configuration=[{
#          "cidrMask": 24,
#          "name": "Public",
#          "subnetType": aws_ec2.SubnetType.PUBLIC,
#        },
#        {
#          "cidrMask": 24,
#          "name": "Private",
#          "subnetType": aws_ec2.SubnetType.PRIVATE
#        },
#        {
#          "cidrMask": 28,
#          "name": "Isolated",
#          "subnetType": aws_ec2.SubnetType.ISOLATED,
#          "reserved": True
#        }
#      ],
      gateway_endpoints={
        "S3": aws_ec2.GatewayVpcEndpointOptions(
          service=aws_ec2.GatewayVpcEndpointAwsService.S3
        )
      }
    )

    sg_use_graph_db = aws_ec2.SecurityGroup(self, "NeptuneClientSG",
      vpc=vpc,
      allow_all_outbound=True,
      description='security group for neptune tutorial client',
      security_group_name='use-neptune-tutorial'
    )
    core.Tag.add(sg_use_graph_db, 'Name', 'use-neptune-tutorial')

    sg_graph_db = aws_ec2.SecurityGroup(self, "NeptuneSG",
      vpc=vpc,
      allow_all_outbound=True,
      description='security group for neptune tutorial',
      security_group_name='neptune-tutorial'
    )
    core.Tag.add(sg_graph_db, 'Name', 'neptune-tutorial')

    sg_graph_db.add_ingress_rule(peer=sg_graph_db, connection=aws_ec2.Port.tcp(8182), description='neptune-tutorial')
    sg_graph_db.add_ingress_rule(peer=sg_use_graph_db, connection=aws_ec2.Port.tcp(8182), description='use-neptune-tutorial')

    graph_db_subnet_group = aws_neptune.CfnDBSubnetGroup(self, "NeptuneTutorialSubnetGroup",
      db_subnet_group_description="subnet group for neptune tutorial",
      subnet_ids=vpc.select_subnets(subnet_type=aws_ec2.SubnetType.PRIVATE).subnet_ids,
      db_subnet_group_name='neptune-tutorial'
    )

    graph_db = aws_neptune.CfnDBCluster(self, "NeptuneTutorial",
      availability_zones=vpc.availability_zones,
      db_subnet_group_name=graph_db_subnet_group.db_subnet_group_name,
      db_cluster_identifier="neptune-tutorial",
      backup_retention_period=1,
      preferred_backup_window="08:45-09:15",
      preferred_maintenance_window="sun:18:00-sun:18:30",
      vpc_security_group_ids=[sg_graph_db.security_group_id]
    )
    graph_db.add_depends_on(graph_db_subnet_group)

    graph_db_instance = aws_neptune.CfnDBInstance(self, "NeptuneTutorialInstance",
      db_instance_class="db.r5.large",
      allow_major_version_upgrade=False,
      auto_minor_version_upgrade=False,
      availability_zone=vpc.availability_zones[0],
      db_cluster_identifier=graph_db.db_cluster_identifier,
      db_instance_identifier="neptune-tutorial",
      preferred_maintenance_window="sun:18:00-sun:18:30"
    )
    graph_db_instance.add_depends_on(graph_db)

    graph_db_replica_instance = aws_neptune.CfnDBInstance(self, "NeptuneTutorialReplicaInstance",
      db_instance_class="db.r5.large",
      allow_major_version_upgrade=False,
      auto_minor_version_upgrade=False,
      availability_zone=vpc.availability_zones[-1],
      db_cluster_identifier=graph_db.db_cluster_identifier,
      db_instance_identifier="neptune-tutorial-replica",
      preferred_maintenance_window="sun:18:00-sun:18:30"
    )
    graph_db_replica_instance.add_depends_on(graph_db)
    graph_db_replica_instance.add_depends_on(graph_db_instance)

