"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from unittest import skip

from simulation.models import Thing, Data, Task
from simulation.simulations import BaseSim
from common.fn import load_fn, class_name

from tastypie.test import ResourceTestCase
from urlparse import urlparse
from simulation.tasks import call_sim_method, call_sim_task_method


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
        Data.save_state(t, sim)
        new_sim = TestSim(t.uuid)
        Data.load_state(t, new_sim)
        self.assertEquals(new_sim.x, 10)
        self.assertEquals(new_sim.z, 'hello')
        self.assertEquals(new_sim.ts, [1, 2, 3, 4])

    def test_load_fn(self):
        for i in xrange(2):
            self.assertEquals(BaseSim, load_fn('simulation.simulations.BaseSim'))


class TestSim2(BaseSim):

    def task_foo(self, task):
        task.status = 'COMPLETED'
        task.save()
        return 'foo'


class TestTask(TestCase):

    def test_defaults(self):
        t = Thing.create_thing(sim_class=TestSim2)
        t.save()
        self.task = Task(thing=t, name='foo')
        self.task.save()
        id = self.task.id

        task2 = Task.objects.get(id=id)
        self.assertEquals(task2.thing, t)
        self.assertEquals(task2.kwargs, {})
        self.assertEquals(task2.result, None)
        self.assertEquals(task2.name, 'foo')
        self.assert_(task2.authorization)
        self.assertEquals(len(task2.authorization), 64)
        self.assertEquals(task2.result, None)
        self.assertEquals(task2.status, 'REQUESTED')

    def test_call_method(self):
        self.test_defaults()
        task2 = Task.objects.get(id=self.task.id)
        self.assertEquals(task2.result, None)
        self.assertEquals(task2.status, 'REQUESTED')
        task2.call_sim_method()
        task3 = Task.objects.get(id=self.task.id)
        self.assertEquals(task3.result, 'foo')
        self.assertEquals(task3.status, 'COMPLETED')


class TestRobotResource(ResourceTestCase):

    def setUp(self):
        super(TestRobotResource, self).setUp()

        # Create a user.
        self.username = 'test'
        self.password = 'pass'
        self.user = User.objects.create_user(self.username, 'test@example.com', self.password)

        self.thing = Thing.create_thing(sim_class=TestSim2)
        self.thing.save()

        # We also build a detail URI, since we will be using it all over.
        # DRY, baby. DRY.
        self.detail_url = '/leaf_api/v1/robot2/{0}/'.format(self.thing.pk)

        # The data we'll send on POST requests. Again, because we'll use it
        # frequently (enough).
        self.post_data = {
            'user': '/api/v1/user/{0}/'.format(self.user.pk),
            'title': 'Second Post!',
            'slug': 'second-post',
            'created': '2012-05-01T22:05:12'
        }

        self.args = dict(format='json', authentication=self.get_credentials(), HTTP_AUTHORIZATION_KEY=self.thing.authorization)

    def get_credentials(self):
        return self.create_basic(username=self.username, password=self.password)

    def test_get_list_unauthorzied(self):
        self.assertHttpUnauthorized(self.api_client.get('/leaf_api/v1/robot2/', format='json'))

    def test_get_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.get(self.detail_url, format='json'))

    def test_get_detail_no_auth_key(self):
        self.assertHttpUnauthorized(self.api_client.get(self.detail_url, format='json', authentication=self.get_credentials()))

    def test_get_detail_json(self):
        resp = self.api_client.get(self.detail_url, **self.args)
        self.assertValidJSONResponse(resp)

        # We use ``assertKeys`` here to just verify the keys, not all the data.
        data = self.deserialize(resp)
        self.assertKeys(data, [u'alias', u'authorization', u'resource_uri', u'uuid'])
        self.assertEqual(data['alias'], None)
        self.assertEqual(data['authorization'], self.thing.authorization)
        self.assertEqual(data['resource_uri'], self.detail_url)
        self.assertEqual(data['uuid'], self.thing.pk)


class TestTaskResource(ResourceTestCase):

    maxDiff = None

    def setUp(self):
        super(TestTaskResource, self).setUp()

        # Create a user.
        self.username = 'test'
        self.password = 'pass'
        self.user = User.objects.create_user(self.username, 'test@example.com', self.password)

        self.robot = Thing.create_thing(sim_class=TestSim2)
        self.robot.save()
        self.task = Task(thing=self.robot, name='foo')
        self.task.save()

        # We also build a detail URI, since we will be using it all over.
        # DRY, baby. DRY.
        self.detail_url = '/leaf_api/v1/task/{0}/'.format(self.task.pk)

        # The data we'll send on POST requests. Again, because we'll use it
        # frequently (enough).
        self.post_data = {
            'robot': self.robot.uuid,
            'name': 'foo',
        }

        self.task_args = dict(format='json', authentication=self.get_credentials(), HTTP_AUTHORIZATION_KEY=self.task.authorization)
        self.robot_args = dict(format='json', authentication=self.get_credentials(), HTTP_AUTHORIZATION_KEY=self.robot.authorization)

    def get_credentials(self):
        return self.create_basic(username=self.username, password=self.password)

    def test_get_list_unauthorzied(self):
        self.assertHttpUnauthorized(self.api_client.get('/leaf_api/v1/task/', format='json'))

    def test_get_list_json(self):
        resp = self.api_client.get('/leaf_api/v1/task/', **self.task_args)
        self.assertValidJSONResponse(resp)

        # Scope out the data for correctness.
        data = self.deserialize(resp)
        self.assertEqual(len(data['objects']), 1)
        # Here, we're checking an entire structure for the expected data.
        self.assertEqual(data['objects'][0], {
            u'task': str(self.task.pk),
            u'authorization': self.task.authorization,
            u'kwargs': u'{}',
            u'id': self.task.pk,
            u'name': u'foo',
            u'result': None,
            u'status': u'REQUESTED',
            u'robot': self.task.thing.uuid,
            u'resource_uri': '/leaf_api/v1/task/{0}/'.format(self.task.pk),
            u'task': str(self.task.pk),
        })

    def test_get_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.get(self.detail_url, format='json'))

    def test_get_detail_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get(self.detail_url, format='json', authentication=self.get_credentials()))

    def test_get_detail_json(self):
        resp = self.api_client.get(self.detail_url, **self.task_args)
        self.assertValidJSONResponse(resp)

        data = self.deserialize(resp)

        # We use ``assertKeys`` here to just verify the keys, not all the data.
        self.assertKeys(data, [u'authorization',
                                                 u'id',
                                                 u'kwargs',
                                                 u'name',
                                                 u'resource_uri',
                                                 u'result',
                                                 u'status',
                                                 u'task',
                                                 u'robot'])
        self.assertEqual(data['name'], 'foo')
        self.assertEqual(data['authorization'], self.task.authorization)
        self.assertEqual(data['resource_uri'], self.detail_url)
        self.assertEqual(data['result'], None)
        self.assertEqual(data['status'], u'REQUESTED')
        self.assertEqual(data['robot'], self.task.thing.uuid)

    def test_post_list_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.post('/leaf_api/v1/task/', format='json', data=self.post_data))

    def test_post_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.post('/leaf_api/v1/task/', format='json', data=self.post_data, authentication=self.get_credentials()))

    def test_post_list(self):
        # Check how many are there first.
        self.assertEqual(Task.objects.count(), 1)
        resp = self.api_client.post('/leaf_api/v1/task/', data=self.post_data, **self.robot_args)
        new_task = Task.objects.all()[1]
        url = urlparse(resp._headers['location'][1]).path
        self.assertHttpCreated(resp)
        # Verify a new one has been added.
        self.assertEqual(Task.objects.count(), 2)
        resp = self.api_client.get(url, **self.robot_args)
        self.assertValidJSONResponse(resp)
        data = self.deserialize(resp)
        self.assertEqual(data['name'], 'foo')
        self.assertEqual(data['authorization'], self.robot.authorization)
        self.assertEqual(data['resource_uri'], '/leaf_api/v1/task/{0}/'.format(new_task.id))
        self.assertEqual(data['result'], 'foo')
        self.assertEqual(data['status'], u'COMPLETED')
        self.assertEqual(data['robot'], self.task.thing.uuid)

    def test_put_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.put(self.detail_url, format='json', data={}))

    def test_put_detail_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.put(self.detail_url, format='json', data={}, authentication=self.get_credentials()))

    @skip('')
    def test_put_detail(self):
        # Grab the current data & modify it slightly.
        original_data = self.deserialize(self.api_client.get(self.detail_url, format='json', authentication=self.get_credentials()))
        return
        new_data = original_data.copy()
        new_data['title'] = 'Updated: First Post'
        new_data['created'] = '2012-05-01T20:06:12'

        self.assertEqual(Task.objects.count(), 5)
        self.assertHttpAccepted(self.api_client.put(self.detail_url, format='json', data=new_data, authentication=self.get_credentials()))
        # Make sure the count hasn't changed & we did an update.
        self.assertEqual(Task.objects.count(), 5)
        # Check for updated data.
        self.assertEqual(Task.objects.get(pk=25).title, 'Updated: First Post')
        self.assertEqual(Task.objects.get(pk=25).slug, 'first-post')
        self.assertEqual(Task.objects.get(pk=25).created, datetime.datetime(2012, 3, 1, 13, 6, 12))

    def test_delete_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.delete(self.detail_url, format='json'))

    @skip('')
    def test_delete_detail(self):
        self.assertEqual(Task.objects.count(), 1)
        self.assertHttpAccepted(self.api_client.delete(self.detail_url, **self.task_args))
        self.assertEqual(Task.objects.count(), 0)


class HelloRobot(BaseSim):

    def sim_hello(self):
        return "Hello"

    def sim_task_hello(self, task):
        task.status = 'COMPLETED'
        task.save()
        return "Hello"


class TestCallSimMethod(TestCase):

    def test_call(self):
        sim = Thing.create_sim(HelloRobot)
        self.assertEquals(sim.sim_hello(), 'Hello')

    def test_sim_call(self):
        sim = Thing.create_sim(HelloRobot)
        self.assertEquals(call_sim_method(sim.uuid, 'sim_hello'), 'Hello')

    def test_sim_task_call(self):
        sim = Thing.create_sim(HelloRobot)
        task = Task(thing=Thing.objects.get(uuid=sim.uuid), name='hello')
        task.save()
        task2 = Task.objects.get(id=task.id)
        self.assertEquals(task2.status, 'REQUESTED')
        self.assertEquals(call_sim_task_method(sim.uuid, task.id, 'sim_task_hello'), 'Hello')
        task2 = Task.objects.get(id=task.id)
        self.assertEquals(task2.status, 'COMPLETED')
