
import celery

from simulation.simulations import Robot as RobotSim
from leaf.models import Robot

@celery.task
def create_robot():
    sim = RobotSim.create_sim()
    robot = Robot(uuid=sim.uuid)
    robot.save()

