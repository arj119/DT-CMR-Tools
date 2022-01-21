import numpy as np
import pandas as pd
import scipy.stats as st

column_ending = '_12_seg'
supported_diffusion_parameters = ['E1', 'E2', 'E3', 'FA', 'MD', 'MODE',
                                  'HA', 'E2A', 'IA', 'TA', 'HA_lg', 'WALL_THICKNESS', 'HA_lg * WT / 100',
                                  'HA_range', 'HA_bins', 'IA_bins', 'E2A_bins']


def __flatten__(list):
    return [item for sublist in list for item in sublist]


# Data analysis class for diffusion parameter data
class DiffusionParameterData:
    def __init__(self):
        self.patient_entries = {}
        self.patient_global = {}

    # Sets class members
    def add_data(self, data, patient_identifier):
        if patient_identifier not in self.patient_entries:
            raw = {key.replace(column_ending, ""): value for (key, value) in data.items() if
                   key.endswith(column_ending)}
            diffusion_parameters = {key: self.get_diffusion_parameter(key, raw) for key in raw.keys() if
                                    key in supported_diffusion_parameters + ['HA_lp']}

            self.patient_entries[patient_identifier] = diffusion_parameters
            self.patient_global[patient_identifier] = range(0, 12)
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
        if param_name == "HA_lp":
            for i in regions:
                values.append(diffusion_param.at[i, 'values'])
        else:
            for i in regions:
                if diffusion_param.at[i, 'values'] != []:
                    values.append(diffusion_param.at[i, 'values'][0].tolist())
        return __flatten__(values)

    # Returns a combined list of values for a diffusion parameter given patients and their regions
    def get_combined_param_values(self, param_name, patient_to_regions):
        values = []
        for patient_identifier, regions in patient_to_regions.items():
            values.append(self.get_parameter_regions_values(param_name, regions, patient_identifier))
        return __flatten__(values)

    # Returns a flat numpy array of diffusion parameter values of a given patients and their regions
    def get_combined_param_values_array(self, param_name, patient_to_regions):
        if param_name == 'HA_lg * WT / 100':
            dpv_HA_lg = np.array(self.get_combined_param_values('HA_lg', patient_to_regions))
            dpv_WALL_THICKNESS = np.array(self.get_combined_param_values('WALL_THICKNESS', patient_to_regions))
            diffusion_param_values = np.multiply(dpv_HA_lg, dpv_WALL_THICKNESS) / 100

        elif param_name == "HA_range":
            dpv_HA_lp = self.get_combined_param_values('HA_lp', patient_to_regions)
            diffusion_param_values = np.array(np.mean(dpv_HA_lp, axis=0)) if len(dpv_HA_lp) else []

        elif param_name == "HA_bins":
            diffusion_param_values = np.array(self.get_combined_param_values("HA", patient_to_regions)) if len(
                self.get_combined_param_values("HA", patient_to_regions)) != 0 else []

        elif param_name == "IA_bins":
            diffusion_param_values = np.array(self.get_combined_param_values("IA", patient_to_regions)) if len(
                self.get_combined_param_values("IA", patient_to_regions)) != 0 else []

        elif param_name == "E2A_bins":
            diffusion_param_values = np.array(self.get_combined_param_values("E2A", patient_to_regions)) if len(
                self.get_combined_param_values("E2A", patient_to_regions)) != 0 else []

        else:
            diffusion_param_values = np.array(self.get_combined_param_values(param_name, patient_to_regions))
        return diffusion_param_values

    # Returns a summary entry for given diffusion parameter for each patient and the selected regions
    def get_combined_param_region_summary(self, param_name, patient_to_regions):
        diffusion_param_values = self.get_combined_param_values_array(param_name, patient_to_regions)

        if param_name == 'E2A' or param_name == 'TA':
            diffusion_param_values = np.absolute(diffusion_param_values)

        # Calculate data points
        param_values_as_series = pd.Series(diffusion_param_values)
        mean = param_values_as_series.mean()
        std = param_values_as_series.std()
        quartiles = st.mstats.mquantiles(diffusion_param_values, [.25, .5, .75], alphap=0.5, betap=0.5)
        summary = [param_name, mean, std, quartiles[1], quartiles[2] - quartiles[0], quartiles[0], quartiles[2]]

        # Scale if necessary
        scale_params = ['E1', 'E2', 'E3']
        if param_name in scale_params:
            for i in range(1, len(summary)):
                summary[i] = summary[i] * 1000

        # if the parameter is HA_range, return also the min and max
        if param_name == 'HA_range':
            min_HA_range = param_values_as_series.min()
            max_HA_range = param_values_as_series.max()
            return summary, [min_HA_range, max_HA_range]

        elif param_name == "HA_bins":
            LHC, CHC, RHC = 0, 0, 0
            if param_values_as_series.size != 0:
                LHC = param_values_as_series[(-90 <= param_values_as_series) & (
                        param_values_as_series < -30)].count() / param_values_as_series.size
                CHC = param_values_as_series[(-30 <= param_values_as_series) & (
                        param_values_as_series <= 30)].count() / param_values_as_series.size
                RHC = param_values_as_series[(30 < param_values_as_series) & (
                        param_values_as_series <= 90)].count() / param_values_as_series.size
            return summary, [LHC, CHC, RHC]

        elif param_name == "IA_bins":
            LHC, CHC, RHC = 0, 0, 0
            if param_values_as_series.size != 0:
                LHC = param_values_as_series[(-90 <= param_values_as_series) & (
                        param_values_as_series < -30)].count() / param_values_as_series.size
                CHC = param_values_as_series[(-30 <= param_values_as_series) & (
                        param_values_as_series <= 30)].count() / param_values_as_series.size
                RHC = param_values_as_series[(30 < param_values_as_series) & (
                        param_values_as_series <= 90)].count() / param_values_as_series.size
            return summary, [LHC, CHC, RHC]

        elif param_name == "E2A_bins":
            LHC, CHC, RHC = 0, 0, 0
            if param_values_as_series.size != 0:
                LHC = param_values_as_series[(-90 <= param_values_as_series) & (
                        param_values_as_series < -30)].count() / param_values_as_series.size
                CHC = param_values_as_series[(-30 <= param_values_as_series) & (
                        param_values_as_series <= 30)].count() / param_values_as_series.size
                RHC = param_values_as_series[(30 < param_values_as_series) & (
                        param_values_as_series <= 90)].count() / param_values_as_series.size
            return summary, [LHC, CHC, RHC]

        return summary, None

    # Returns a summary panda data frame for all diffusion parameters in the given dictionary of
    # patient identifiers to regions
    def get_combined_patient_regions_summary(self, patient_to_regions):
        columns = ['Diffusion Parameter', 'Mean', 'Standard Deviation', 'Median', 'Interquartile Range',
                   'Lower Quartile', 'Upper Quartile']
        data = []
        for parameter in supported_diffusion_parameters:
            parameter_summary, extra_info = self.get_combined_param_region_summary(parameter, patient_to_regions)
            if parameter_summary[0] == 'HA_range' and not np.isnan(extra_info).any():
                HA_min_max = extra_info
                parameter_summary[1] = f'min: {HA_min_max[0]:.2f}'
                parameter_summary[2] = f'max: {HA_min_max[1]:.2f}'
                parameter_summary[3] = f'range: {(HA_min_max[1] - HA_min_max[0]):.2f}'
                parameter_summary[4:] = ""

            elif parameter_summary[0] == "HA_bins" and extra_info != [0, 0, 0]:
                LHC, CHC, RHC = extra_info
                parameter_summary[1] = f'LHC: {LHC * 100:.2f}%'
                parameter_summary[2] = f'CHC: {CHC * 100:.2f}%'
                parameter_summary[3] = f'RHC: {RHC * 100:.2f}%'
                parameter_summary[4:] = ""

            elif parameter_summary[0] == "IA_bins" and extra_info != [0, 0, 0]:
                LHC, CHC, RHC = extra_info
                parameter_summary[1] = f'LHC: {LHC * 100:.2f}%'
                parameter_summary[2] = f'CHC: {CHC * 100:.2f}%'
                parameter_summary[3] = f'RHC: {RHC * 100:.2f}%'
                parameter_summary[4:] = ""

            elif parameter_summary[0] == "E2A_bins" and extra_info != [0, 0, 0]:
                LHC, CHC, RHC = extra_info
                parameter_summary[1] = f'LHC: {LHC * 100:.2f}%'
                parameter_summary[2] = f'CHC: {CHC * 100:.2f}%'
                parameter_summary[3] = f'RHC: {RHC * 100:.2f}%'
                parameter_summary[4:] = ""

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
