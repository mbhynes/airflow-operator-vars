# airflow-operator-vars

This repository shows a minimal working example of how to set up an extensible airflow operator class that streamlines how you *should* use airflow [Variables](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/variables.html) to modify task context at execution time.

## Why

Because often you need flexibility in some of a DAG's parameters to deal with finicky external factors environment. It's not uncommon that  something goes awry and you need a hotfix to change some simple DAG parameters---but if your organization's deployment pipeline is slow or clunky it can be really painful to make that hotfix.

Variables look like they're *exactly* what you need---perfect! You start using them. Fast-foward a few months and egad everyone on your team is sticking them everywhere willy nilly, and naming them inconsistently and polluting the global scope. Welcome to software: your solution now needs solution.

## What

This repo has an example `VariableOverrideOperator` class that's an example of how airflow variables can be systematized by:
- requiring a fixed JSON-formatted nested payload stucture, where:
   - each DAG has 1 (`dict`) variable, named exactly after its `dag_id`
   - each DAG's tasks have 1 nested `dict` entry in the DAG `dict` variable, keyed by `task_id`
- rolling out a `pre_execute()` method on the `VariableOverrideOperator` that retrieves the DAG's variable and dynamically overrides the operator's attributes with any corresponding values from the variable

## Example

Check out the following toy example operator that prints out some attributes to the logs:
https://github.com/mbhynes/airflow-operator-vars/blob/b771c21bd7bde448b25ce4051fdd3287096b55d3/varops/dags/overridable_dag.py#L6-L24

We can modify its runtime behaviour by creating and editing a variable with keys to match the `(dag_id, task_id)` key system:
![airflow-overrides](https://user-images.githubusercontent.com/10452129/227689774-cedc30e3-8b3b-4063-a35e-4d12807a5958.gif)

## How

Just a few simple lines, nothing fancy:

https://github.com/mbhynes/airflow-operator-vars/blob/main/varops/operators/base.py#L63-L90
