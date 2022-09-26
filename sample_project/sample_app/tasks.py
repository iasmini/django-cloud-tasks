from django_cloud_tasks.tasks import PeriodicTask, RoutineTask, SubscriberTask, Task


class BaseAbstractTask(Task):
    abstract = True

    def run(self, **kwargs):
        raise NotImplementedError()  # TODO Allow inheriting from ABC


class AnotherBaseAbstractTask(BaseAbstractTask):
    abstract = True

    def run(self, **kwargs):
        raise NotImplementedError()


class CalculatePriceTask(Task):
    def run(self, price, quantity, discount):
        return price * quantity * (1 - discount)


class FailMiserablyTask(AnotherBaseAbstractTask):
    only_once = True

    def run(self, magic_number):
        return magic_number / 0


class SaySomethingTask(PeriodicTask):
    run_every = "* * * * 1"

    def run(self):
        print("Hello!!")


class PleaseNotifyMeTask(SubscriberTask):
    enable_message_ordering = True

    @property
    def topic_name(self):
        return "potato"

    @property
    def dead_letter_topic_name(self):
        return None

    def run(self, message, attributes):
        return print(message)


class SayHelloTask(RoutineTask):
    def run(self, **kwargs):
        return {"message": "hello"}

    def revert(self, data: dict):
        return {"message": "goodbye"}


class SayHelloWithParamsTask(RoutineTask):
    def run(self, spell: str):
        return {"message": spell}

    def revert(self, data: dict):
        return {"message": "goodbye"}
