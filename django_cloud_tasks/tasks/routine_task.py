import logging
from typing import Dict
from abc import abstractmethod
from django_cloud_tasks import models, tasks

logger = logging.getLogger()

class RoutineTask(tasks.Task):
    abstract = True

    @abstractmethod
    def run(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def revert(self, data: Dict, _meta: Dict, **kwargs):
        routine = models.Routine.objects.get(pk=_meta.get("routine_id"))
        routine.status = models.Routine.Statuses.REVERTED
        routine.save()

class PipelineRoutineTask(tasks.Task):
    def run(self, routine_id: int):
        routine = models.Routine.objects.get(pk=routine_id)
        if routine.status == models.Routine.Statuses.COMPLETED:
            logger.info(f"Routine #{routine_id} is already completed")
            return

        if routine.max_retries and routine.attempt_count >= routine.max_retries:
            logger.info(f"Routine #{routine_id} has exhausted retries and is being reverted")
            routine.pipeline.revert()
            return

        routine.attempt_count += 1
        routine.status = models.Routine.Statuses.RUNNING
        routine.save()

        try:
            logger.info(f"Routine #{routine_id} is running")
            task_response = routine.task().run(**routine.body)
        except Exception as e:
            logger.info(f"Routine #{routine_id} has failed")
            routine.fail(output={"error": str(e)})
            routine.enqueue()
            logger.info(f"Routine #{routine_id} has been enqueued for retry")
            return

        routine.complete(output=task_response)
        logger.info(f"Routine #{routine_id} just completed")
