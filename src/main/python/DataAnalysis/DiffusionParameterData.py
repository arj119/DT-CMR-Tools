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
        self.patient_entries = {}
        self.patient_global = {}
        self.summary = pd.DataFrame()

    def __call__(self):
        return self.summary

    # Sets class members
    def add_data(self, data, patient_identifier):
        if patient_identifier not in self.patient_entries:
            raw = {key.replace(column_ending, ""): value for (key, value) in data.items() if
                   key.endswith(column_ending)}
            diffusion_parameters = {key: self.get_diffusion_parameter(key, raw) for key in raw.keys() if
                                    key in supported_diffusion_parameters}

            self.patient_entries[patient_identifier] = diffusion_parameters
            self.patient_global[patient_identifier] = range(0, 12)
            self.summary = self.get_regions_summary(range(0, 12), patient_identifier)
        return self.get_combined_global_summary()

    # Gets diffusion parameter
    def get_diffusion_parameter(self, param_name, raw):
        data = raw[param_name]
        param_frame = pd.DataFrame(data[-1])
        return param_frame

    # Returns flat list of collective values for a given parameter and specified regions
    def get_parameter_regions_values(self, param_name, regions, patient_identifier):
        diffusion_param = self.patient_entries[patient_identifier][param_name]
        values = []
        for i in regions:
            values.append(diffusion_param.at[i, 'values'][0].tolist())
        return __flatten__(values)

    # Returns a combined list of values for a diffusion parameter given patients and their regions
    def get_combined_param_values(self, param_name, patient_to_regions):
        values = []
        for patient_identifier, regions in patient_to_regions.items():
            values.append(self.get_parameter_regions_values(param_name, regions, patient_identifier))
        return __flatten__(values)

    # Returns a summary entry for given diffusion parameter for each patient and the selected regions
    def get_combined_param_region_summary(self, param_name, patient_to_regions):
        diffusion_param_values = np.array(self.get_combined_param_values(param_name, patient_to_regions))
        if param_name == "E2A":
            diffusion_param_values = np.absolute(diffusion_param_values)

        # Calculate data points
        param_values_as_series = pd.Series(diffusion_param_values)
        mean = param_values_as_series.mean()
        std = param_values_as_series.std()
        quartiles = param_values_as_series.quantile([.25, .5, .75]).to_numpy()
        summary = [param_name, mean, std, quartiles[1], quartiles[2] - quartiles[0], quartiles[0], quartiles[2]]

        # Scale if necessary
        scale_params = ['E1', 'E2', 'E3']
        if param_name in scale_params:
            for i in range(1, len(summary)):
                summary[i] = summary[i] * 1000
        return summary

    # Returns a summary panda data frame for all diffusion parameters in the given dictionary of
    # patient identifiers to regions
    def get_combined_patient_regions_summary(self, patient_to_regions):
        columns = ['Diffusion Parameter', 'Mean', 'Standard Deviation', 'Median', 'Interquartile Range',
                   'Lower Quartile', 'Upper Quartile']
        data = []
        for parameter in supported_diffusion_parameters:
            parameter_summary = self.get_combined_param_region_summary(parameter, patient_to_regions)
            data.append(parameter_summary)
        return pd.DataFrame(data, columns=columns)

    # Returns a summary panda data frame for all diffusion parameters in the given dictionary of
    # all patient identifiers
    def get_combined_global_summary(self):
        return self.get_combined_patient_regions_summary(self.patient_global)

    # Returns a summary panda data frame for all diffusion parameters in the given regions of the given patient
    def get_regions_summary(self, regions, patient_identifier):
        return self.get_combined_patient_regions_summary({patient_identifier: regions})

    # Removes patient data
    def remove_patient_data(self, patient_identifier):
        self.patient_entries.pop(patient_identifier)
        self.patient_global.pop(patient_identifier)
