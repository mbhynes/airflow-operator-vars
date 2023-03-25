from datetime import datetime, timedelta

from airflow import DAG

from varops.operators.base import VariableOverrideOperator


class ExampleOverrideOperator(VariableOverrideOperator):
    override_attrs = {"email", "sender"}
    override_callables = {"email": lambda val, context: val.reverse()}

    def __init__(self, name, email, sender, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.email = email
        self.sender = sender

    def execute(self, context):
        self.log.info(f"Sending email to {self.email} from {self.sender}")
        return 0

dag = DAG(
     dag_id="overridable_dag",
     start_date=datetime.utcnow(),
     catchup=False,
     schedule=timedelta(minutes=2),
)

with dag:
    task1 = ExampleOverrideOperator(task_id="task1", name="mike", email="mike@hello.com", sender="airflow")
    task2 = ExampleOverrideOperator(task_id="task2", name="bob", email="bob@hello.com", sender="airflow")
    task1.set_downstream(task2)
