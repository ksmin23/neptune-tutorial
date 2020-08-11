#!/usr/bin/env python3

from aws_cdk import core

from neptune_tutorial.neptune_tutorial_stack import NeptuneTutorialStack


app = core.App()
NeptuneTutorialStack(app, "neptune-tutorial")

app.synth()
