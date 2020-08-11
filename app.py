#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab

from aws_cdk import core

from neptune_tutorial.neptune_tutorial_stack import NeptuneTutorialStack


app = core.App()
NeptuneTutorialStack(app, "neptune-tutorial")

app.synth()
