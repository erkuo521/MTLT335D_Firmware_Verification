class Test_Criteria:

    def __init__(self):


    def on_evlaluate():
        raise NotImplementedError("Subclass must implement abstract method")


class ExactMatch(Test_Criteria):

    def __init__(self, expected_result):
        self.actual = None
        self.expected = expected_result
        self.result = False

    def on_evaluate(actual_result):
        self.actual = actual_result
