from simulation.IPAROSimulationEnvironment import IPAROSimulationEnvironment
from simulation.Operation import LatestOperation, StoreOperation, FirstOperation, GetAtTOperation, GetNthOperation, \
    ListAllOperation

# URL doesn't matter much, but the fact that it exists is important.
URL = "example.com"


class IPAROSimulation:

    def __init__(self, env: IPAROSimulationEnvironment):
        self.env = env

    def run(self):
        # Create some storage.
        env = self.env

        if env.verbose:
            print("Storing nodes...")

        # Link the IPAROs in the IPFS
        store_op = StoreOperation(env)
        store_op.execute()
        # for operation in self.environment.operations:
        #     self.dispatch(operation)

        if env.verbose:
            print("Applying other operations...")

        first_op = FirstOperation(env)
        first_op.execute()
        for op in env.operations:
            self.dispatch(op)


    def dispatch(self, operation: str):
        op = None
        match operation.lower():
            case "time":
                op = GetAtTOperation(self.env)
            case "nth":
                op = GetNthOperation(self.env)
            case "first":
                op = FirstOperation(self.env)
            case "latest":
                op = LatestOperation(self.env)
            case "list":
                op = ListAllOperation(self.env)
        if op is not None:
            op.execute()
