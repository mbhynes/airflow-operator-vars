from airflow import DAG

from ..operators.base import VariableOverrideOperator


class ExampleOverrideOperator(VariableOverrideOperator):
    override_attrs = {"email", "sender"}

    def __init__(self, name, email, sender, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.email = email
        self.sender = sender

    def execute(self, context):
        self.log.info(f"Sending email to {self.email} from {self.sender}")
        return 0

dag = DAG()

with dag:
    task1 = ExampleOverrideOperator(name="mike", email="mike@hello.com", sender="airflow")
    task2 = ExampleOverrideOperator(name="bob", email="bob@hello.com", sender="airflow")
    task1.set_downstream(task2)
