import pandas as pd
import numpy as np

column_ending = '_12_seg'
supported_diffusion_parameters = ['E1', 'E2', 'E3', 'FA', 'MD', 'MODE',
                                  'HA', 'E2A', 'IA']


def __flatten__(list):
    return [item for sublist in list for item in sublist]


class DiffusionParameterData:
    def __init__(self, data):
        self.raw_data = {key.replace(column_ending, ""): value for (key, value) in data.items() if
                         key.endswith(column_ending)}
        self.diffusion_parameters = {key: self.get_parameter(key) for key in self.raw_data.keys() if
                                     key in supported_diffusion_parameters}

        self.summary = self.get_summary_segments(range(0, 12))

    def __call__(self):
        return self.summary

    def get_parameter(self, param_name):
        data = self.raw_data[param_name]
        param_frame = pd.DataFrame(data[-1])
        return param_frame

    def calculate_parameter_means(self, param_name):
        diffusion_param = self.diffusion_parameters[param_name]
        if 'mean' in diffusion_param.columns:
            return diffusion_param['mean']
        else:
            for i in range(0, 12):
                diffusion_param.at[i, 'mean'] = (diffusion_param.at[i, 'values'].mean())
            return diffusion_param['mean']

    def calculate_parameter_sds(self, param_name):
        diffusion_param = self.diffusion_parameters[param_name]
        if 'sd' in diffusion_param.columns:
            return diffusion_param['sd']
        else:
            for i in range(0, 12):
                diffusion_param.at[i, 'sd'] = (diffusion_param.at[i, 'values'].std())
            return diffusion_param['sd']

    def get_parameter_segment_values(self, param_name, segments):
        diffusion_param = self.diffusion_parameters[param_name]
        values = []
        for i in segments:
            values.append(diffusion_param.at[i, 'values'][0].tolist())
        return np.array(__flatten__(values))

    def get_parameter_segment_summary(self, param_name, segments):
        diffusion_param_values = self.get_parameter_segment_values(param_name, segments)
        param_values_as_series = pd.Series(diffusion_param_values)
        return [param_name, param_values_as_series.mean(), param_values_as_series.std()]

    def get_summary_segments(self, segments):
        columns = ['Diffusion Parameter', 'Mean', 'Standard Deviation']
        data = []
        for parameter in self.diffusion_parameters.keys():
            parameter_summary = self.get_parameter_segment_summary(parameter, segments)
            data.append(parameter_summary)
        return pd.DataFrame(data, columns=columns)
