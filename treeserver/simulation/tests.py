"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from simulation.models import Thing, Data
from simulation.simulations import BaseSim
from common.fn import load_fn, class_name


class TestThing(TestCase):

    def test(self):
        t = Thing()
        t.save()
        self.assertTrue(t.uuid)
        #self.assertTrue(t.tclass)

    def test_class_name(self):
        self.assertEquals("{0}.{1}".format(BaseSim.__module__, BaseSim.__name__), 'simulation.simulations.BaseSim')
        self.assertEquals(class_name(BaseSim), 'simulation.simulations.BaseSim')

    def test_create_sim(self):
        self.sim = Thing.create_sim(BaseSim)
        self.assertTrue(self.sim.uuid)
        t = Thing.objects.get(uuid=self.sim.uuid)
        self.assertEquals(t.uuid, self.sim.uuid)

    def test_save_load_sim(self):
        self.test_create_sim()
        self.sim.a = 1
        self.sim.b = 2
        self.sim.c = None
        Thing.save_sim(self.sim)
        new_sim = Thing.load_sim(self.sim.uuid)
        self.assertEquals(new_sim.uuid, self.sim.uuid)
        self.assertEquals(new_sim.a, 1)
        self.assertEquals(new_sim.b, 2)
        self.assertEquals(new_sim.c, None)

class TestSim(BaseSim):

    pass


class TestData(TestCase):

    def test_get_set(self):
        t = Thing()
        t.save()
        Data.set_attribute(t, 'a', 5)
        self.assertEquals(Data.get_attribute(t, 'a'), 5)

    def test_save_load(self):
        t = Thing()
        t.save()
        sim = TestSim(t.uuid)
        sim.x = 10
        sim.z = 'hello'
        sim.ts = [1, 2, 3, 4]
        Data.save_state(t.uuid, sim)
        new_sim = TestSim(t.uuid)
        Data.load_state(t.uuid, new_sim)
        self.assertEquals(new_sim.x, 10)
        self.assertEquals(new_sim.z, 'hello')
        self.assertEquals(new_sim.ts, [1, 2, 3, 4])

    def test_load_fn(self):
        for i in xrange(2):
            self.assertEquals(BaseSim, load_fn('simulation.simulations.BaseSim'))
