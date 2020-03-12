import numpy as np
import pandas as pd

column_ending = '_12_seg'
supported_diffusion_parameters = ['E1', 'E2', 'E3', 'FA', 'MD', 'MODE',
                                  'HA', 'E2A', 'IA']


def __flatten__(list):
    return [item for sublist in list for item in sublist]


# Data analysis class for diffusion parameter data
class DiffusionParameterData:
    def __init__(self):
        self.data = dict
        self.diffusion_parameters = dict
        self.summary = pd.DataFrame()

    def __call__(self):
        return self.summary

    # Sets class members
    def set_data(self, data):
        self.data = {key.replace(column_ending, ""): value for (key, value) in data.items() if
                     key.endswith(column_ending)}
        self.diffusion_parameters = {key: self.get_diffusion_parameter(key) for key in self.data.keys() if
                                     key in supported_diffusion_parameters}
        self.summary = self.get_regions_summary(range(0, 12))
        return self.summary

    # Gets diffusion parameter
    def get_diffusion_parameter(self, param_name):
        data = self.data[param_name]
        param_frame = pd.DataFrame(data[-1])
        return param_frame

    # Updates current data to store means for each diffusion parameter
    def calculate_parameter_means(self, param_name):
        diffusion_param = self.diffusion_parameters[param_name]
        if 'mean' in diffusion_param.columns:
            return diffusion_param['mean']
        else:
            for i in range(0, 12):
                diffusion_param.at[i, 'mean'] = (diffusion_param.at[i, 'values'].mean())
            return diffusion_param['mean']

    # Updates current data to store sd for each diffusion parameter
    def calculate_parameter_sds(self, param_name):
        diffusion_param = self.diffusion_parameters[param_name]
        if 'sd' in diffusion_param.columns:
            return diffusion_param['sd']
        else:
            for i in range(0, 12):
                diffusion_param.at[i, 'sd'] = (diffusion_param.at[i, 'values'].std())
            return diffusion_param['sd']

    # Returns flat list of collective values for a given parameter and specified regions
    def get_parameter_regions_values(self, param_name, regions):
        diffusion_param = self.diffusion_parameters[param_name]
        values = []
        for i in regions:
            values.append(diffusion_param.at[i, 'values'][0].tolist())
        return np.array(__flatten__(values))

    # Returns a summary triple for a given parameter and specified regions
    def get_parameter_regions_summary(self, param_name, regions):
        diffusion_param_values = self.get_parameter_regions_values(param_name, regions)
        param_values_as_series = pd.Series(diffusion_param_values)
        return [param_name, param_values_as_series.mean(), param_values_as_series.std()]

    # Returns a summary panda data frame for all diffusion parameters in the given regions
    def get_regions_summary(self, regions):
        columns = ['Diffusion Parameter', 'Mean', 'Standard Deviation']
        data = []
        for parameter in self.diffusion_parameters.keys():
            parameter_summary = self.get_parameter_regions_summary(parameter, regions)
            data.append(parameter_summary)
        return pd.DataFrame(data, columns=columns)
