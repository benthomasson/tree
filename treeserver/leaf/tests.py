"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from leaf.tasks import create_robot
from leaf.models import Robot
from simulation.simulations import load_sim
from simulation.simulations import Robot as RobotSim


class TestTasks(TestCase):

    def test_create_robot(self):
        create_robot()
        robot = Robot.objects.all()[0]
        sim = load_sim(robot.uuid)
        self.assertEquals(sim.__class__, RobotSim)
        self.assertTrue(robot.uuid)
        self.assertTrue(sim.uuid)
        self.assertEquals(sim.uuid, robot.uuid)
