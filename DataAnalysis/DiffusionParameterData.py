import pandas as pd

column_ending = "_12_seg"


class DiffusionParameterData:
    def __init__(self, data):
        self.data = {key.replace(column_ending, ""): value for (key, value) in data.items() if
                     key.endswith(column_ending)}
        self.diffusionparameters = {key: self.getparameter(key) for key in self.data.keys()}

    def __call__(self):
        return self

    def getparameter(self, param_name):
        data = self.data[param_name]
        paramframe = pd.DataFrame(data[-1])
        return paramframe

    def getparametermean(self, param_name):
        param = self.diffusionparameters[param_name]
        if 'mean' in param.columns:
            return param['mean']
        else:
            for i in range(0, 12):
                param.at[i, 'mean'] = (param.at[i, 'values'].mean())
            return param['mean']

    def getparametersd(self, param_name):
        param = self.diffusionparameters[param_name]
        if 'sd' in param.columns:
            return param['sd']
        else:
            for i in range(0, 12):
                param.at[i, 'sd'] = (param.at[i, 'values'].std())
            return param['sd']
