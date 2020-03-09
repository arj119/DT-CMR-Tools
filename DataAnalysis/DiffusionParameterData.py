import pandas as pd

column_ending = "_12_seg"


class DiffusionParameterData:
    def __init__(self, data):
        self.data = {key.replace(column_ending, ""): value for (key, value) in data.items() if key.endswith(column_ending)}
        self.diffusionparameters = {key: self.getparameter(key) for key in self.data.keys()}
        print(self.diffusionparameters["E2"])

    def __call__(self):
        return self

    def getparameter(self, param_name):
        # if not (param_name.endswith("_12_seg")):
        #     param_name = param_name + "_12_seg"
        # print(param_name)
        data = self.data[param_name]
        paramframe = pd.DataFrame(data[-1])
        return paramframe
