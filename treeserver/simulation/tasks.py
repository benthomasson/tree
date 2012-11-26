
import celery

from simulation.models import Thing, Task

@celery.task
def call_sim_method(thing_id, method_name, *args, **kwargs):
    sim = Thing.load_sim(thing_id)
    assert hasattr(sim, method_name)
    fn = getattr(sim, method_name)
    return fn(*args, **kwargs)


@celery.task
def call_sim_task_method(thing_id, task_id, method_name, *args, **kwargs):
    sim = Thing.load_sim(thing_id)
    task = Task.objects.get(id=task_id)
    assert hasattr(sim, method_name)
    fn = getattr(sim, method_name)
    return fn(task=task, *args, **kwargs)

