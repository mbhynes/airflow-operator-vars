import json

from airflow.models.baseoperator import BaseOperator
from airflow.variable import Variable


class VariableOverrideOperator(BaseOperator):
    """
    An operator with attributes that can be overridden at runtime
    with an airflow Variable for the operator's DAG.

    The purpose of this operator is to provide a simple interface
    for adding operational flexibility to DAGs, such that parameters
    can be overridden at runtime by administrators through the airflow
    CLI or web UI without having to redeploy a DAG.

    
    Variable Format
    ---------------
    The expected format for DAG variable is *fixed* as follows.
    For dag_id="my_dag", the variable should
        - have a JSON-formatted payload of keys matching task_ids
        - the values of the task_id-keyed entries contain the values
          to override the operator's attributes with at runtime.

    The name of the variable can be defined in a child class, but will
    default to the dag_id if unset.

    **Example**: for a dag_id="my_dag" with tasks ["task1", "task2"], an
    valid variable payload to set for Variable.get("my_dag") would be:
    ```
    {
        "task1": {
            "to_email": "override_email@example.com",
            "from_email": "airflow@company.org"
        },
        "task2": {
            "suffix": "_new"
        }
    }
    ```

    How to Subclass
    ---------------
    A subclass of this operator should definte the following class attributes:
        - `override_attrs` (str): a list or set of task attributes to override.
        - `override_callables` (dict): a dict mapping an attribute name to a
            callable of the form `fn(value, context) -> value` that will be called
            to do any preprocessing of the retrieved JSON-encoded value before
            setting the attribute on the operator. If none exists, the raw (desrialed)
            value will be used.
        - `override_var` (str): the name of the variable to retrieve. If unset,
            the dag_id will be used. You probably shouldn't set this.
    """
    override_var = None
    override_attrs = None
    override_callables = None

    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = name

    def pre_execute(self, context):
        """
        Retrieve a json-formatted variable payload for this DAG to override
        this operator's attributes at runtime.
        """
        super().pre_execute(context)

        varname = self.override_var or self.dag_id 

        # Retrieve a json variable payload for this DAG, if it exists
        dag_var = Variable.get(varname, default_var={}, deserialize_json=True)
        if len(dag_var) == 0:
            return

        task_var = dag_var.get(self.task_id, {})
        self.log.debug(f"Retrieved Variable {varname} with payload for task_id='{self.task_id}':")
        self.log.debug(json.dumps(task_var, indent=2))

        overrides = (self.override_attrs or set())
        callables = (self.override_callables or {})

        for attr_key, value in task_var.items():
            if attr_key not in overrides:
                continue
            fn = callables.get(attr_key)
            attr_value = fn(task_var[attr_key], context) if fn is not None else task_var[attr_key]
            self.log.debug(f"Overriding {attr_key} with {attr_value}")
            setattr(self, attr_key, attr_value)
