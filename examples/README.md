# ClawDev Examples

This directory contains example scripts demonstrating how to use the ClawDev framework.

## Running the Examples

To run the examples, make sure you have installed the required dependencies:

```bash
pip install -e .
```

Then run an example script:

```bash
python examples/clawdev_example.py
```

## Example Descriptions

### clawdev_example.py

This example demonstrates the basic usage of the ClawDev framework:

1. Creates an OpenClaw agent
2. Wraps it with an AgentAdapter
3. Creates a ChatChain with the adapter
4. Defines a software development task
5. Runs the complete development chain
6. Cleans up the agent

The example task is to create a simple Python script that calculates the Fibonacci sequence.