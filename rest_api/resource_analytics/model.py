import numpy as np
import pandas as pd
from pymongo import MongoClient
from enum import Enum
from pprint import pprint as pp


class JumpDataType(Enum):
    VELOCITY = 1
    FORCE = 2
    ACCELERATION = 3

class AnalyticsService:
    def __init__(self, 
                 db_url, 
                 db_name, 
                 collection_name) -> None:
        self.client = MongoClient(db_url)
        self.db_name = db_name
        self.collection_name = collection_name
    
    @staticmethod
    def get_cmj_values(vel_csv_file, force_csv_file):
        force_csv = CMJJumpForceCSVReader(force_csv_file)
        vel_csv = CMJJumpVelocityCSVReader(vel_csv_file)
        cmj_jump = CMJJumpModel(force_csv.combined_force, vel_csv.velocity, force_csv.left_force, force_csv.right_force)
        return cmj_jump.get_cmj_data_json()

class SystemWeight:
    def __init__(self, weight, weight_std):
        self.weight = weight
        self.std = weight_std
    
    @classmethod
    def create_from_force_arr(cls, arr):
        head_values = arr[:1000]
        return SystemWeight(head_values.mean(), head_values.std())

class JumpCSVReader:
    def __init__(self, csv_file, csv_header):
        self.csv_file = csv_file
        self.csv_header = csv_header
        self._df = None

    def _verify_columms(self, df_columns, expected_columns):
        """
        Reads only first column of copy and verifies headers
        csv_file: path to file
        columns: list of columns names that needs to be present in csv file header
        """
        missing_cols = []
        for col in expected_columns:
            if col not in df_columns:
                missing_cols.append(col)       
        if missing_cols:
            missing_cols_str = ", ".join(missing_cols)
            raise ValueError(f"Wrong csv headers. No {missing_cols_str} columns.".format(col))
    
    @property
    def df(self):
        if self._df is None:
            self._df = self.create_df()
        return self._df

    def create_df(self):
        """
        Generates dataframe from csv file provided as attribute of object
        :return: pandas dataframe with data from csv file
        """
        df = pd.read_csv(self.csv_file)
        self._verify_columms(df.columns, self.csv_header)
        return df[self.csv_header]


class JumpData:
    """
    Data of jump for physical quantity e.g. force or velocity
    """
    def __init__(self, jump_data_type, time_arr, value_arr, value_col, time_col = "Time (s)"):
        """
        :param csv_path: path to csv file with data
        :param headers: dictionary with key as attribute (time, velocity, left, combined etc.) and col name as value
        """
        self._jump_data_type = jump_data_type
        self._time_arr = time_arr
        self._value_arr = value_arr
        self._items_count = None
        
    @property
    def jump_data_type(self):
        return self._jump_data_type

    @property
    def time_arr(self):
        return self._time_arr
    
    @property
    def value_arr(self):
        return self._value_arr

    @property 
    def items_count(self):
        if self._items_count is None:
            self._items_count = self.set_items_count()
        return self._items_count

    def set_items_count(self):
        time_count = len(self.time_arr)
        values_count = len(self.value_arr)
        if time_count != values_count:
            raise ValueError("Times and values array are of different length")
        return values_count

class CMJJumpForceCSVReader(JumpCSVReader):
    def __init__(self, csv_file):
        self.jump_data_type = JumpDataType.FORCE
        csv_header = ["Time (s)", "Left (N)", "Right (N)", "Combined (N)"]
        super().__init__(csv_file, csv_header)
        self._set_jump_data()

    def _set_jump_data(self):
        self.left_force = JumpData(JumpDataType.FORCE,
                                self.df[self.csv_header[0]].to_numpy(),
                                self.df[self.csv_header[1]].to_numpy(),
                                self.csv_header[1])
        self.right_force = JumpData(JumpDataType.FORCE,
                                self.df[self.csv_header[0]].to_numpy(),
                                self.df[self.csv_header[2]].to_numpy(),
                                self.csv_header[2])
        self.combined_force = JumpData(JumpDataType.FORCE,
                                self.df[self.csv_header[0]].to_numpy(),
                                self.df[self.csv_header[3]].to_numpy(),
                                self.csv_header[3])
                                    
class CMJJumpVelocityCSVReader(JumpCSVReader):
    def __init__(self, csv_file):
        self.jump_data_type = JumpDataType.VELOCITY
        csv_header = ["Time (s)", "Velocity (M/s)"]
        super().__init__(csv_file, csv_header)
        self._set_jump_data()

    def _set_jump_data(self):
        self.velocity = JumpData(JumpDataType.VELOCITY,
                                    self.df[self.csv_header[0]].to_numpy(),
                                    self.df[self.csv_header[1]].to_numpy(),
                                    self.csv_header[1]) 

class JumpModel:
    def __init__(self):
        self.gravity_acc = 9.81        

class CMJJumpModel(JumpModel):
    def __init__(self, combined_force_data: JumpData, vel_data: JumpData, left_force_data: JumpData, right_force_data: JumpData):
        super().__init__()
        self._system_weight = None
        self.combined_force_data = combined_force_data
        self.vel_data = vel_data
        self.left_force_data = left_force_data
        self.right_force_data = right_force_data
        self._acc_data = None

    @property
    def system_weight(self):
        if self._system_weight is None:
            mean = self.combined_force_data.value_arr[:1000].mean()
            std = self.combined_force_data.value_arr[:1000].std()
            self._system_weight = SystemWeight(mean, std)
        return self._system_weight

    @property
    def acc_data(self):
        if self._acc_data is None:
            acc_diff = np.diff(self.vel_data.value_arr, prepend=0) / np.diff(self.vel_data.time_arr, prepend=0)
            self._acc_data = JumpData(JumpDataType.ACCELERATION, self.vel_data.time_arr, acc_diff, "Acceleration (m/s^2)")
        return self._acc_data
    
    def _get_phases_idxs(self):
        if self.combined_force_data.items_count != self.vel_data.items_count:
            raise ValueError("Forces data and velocity data have different lengths.")
        
        ind_unwght_start = -1
        ind_unwght_end = -1
        ind_brk_start = -1
        ind_brk_end = -1
        ind_prop_start = -1
        ind_prop_end = -1

        it = np.nditer([self.combined_force_data.value_arr, self.vel_data.value_arr], flags=["c_index"])
        for x in it:
            # unweighting phase start
            if ind_unwght_start < 0 and  x[0] < self.system_weight.weight - 5 * self.system_weight.std:
                ind_unwght_start = max(0, it.index - 30)  # minus 30 ms suggested by paper

            # braking phase start when force equals to force in silent phase (weight of athlete)
            if ind_unwght_start > 0 and ind_brk_start < 0:  # in unweighting phase (set ind) and ind_brk not set
                if x[0] >= self.system_weight.weight:
                    ind_brk_start = it.index
                ind_unwght_end = ind_brk_start - 1

            if ind_brk_start > 0 and ind_prop_start < 0:
                if x[1] >= 0.01:
                    ind_prop_start = it.index
                ind_brk_end = ind_prop_start - 1

            if ind_prop_start > 0 and ind_prop_end < 0:
                if x[0] < 10:
                    ind_prop_end = it.index

        return {"unweighting": (ind_unwght_start, ind_unwght_end),
                "braking": (ind_brk_start, ind_brk_end),
                "propulsive": (ind_prop_start, ind_prop_end)}


    def get_cmj_stats(self):
        idxs = self._get_phases_idxs()
        ind_unwght_start = idxs["unweighting"][0]
        ind_unwght_end = idxs["unweighting"][1]
        ind_brk_start = idxs["braking"][0]
        ind_brk_end = idxs["braking"][1]
        ind_prop_start = idxs["propulsive"][0]
        ind_prop_end = idxs["propulsive"][1]
        v_peak_prop_idx = np.argmax(self.vel_data.value_arr[ind_prop_start : ind_prop_end])

        # unweighting phase - ind_unwght_start to ind_unwght_end
        # braking phase - ind_brk_start to ind_brk_end
        # propulsive phase - ind_prop_start to ind_prop_end
        # negative phase - ind_unwght_start to ind_brk_end
        # positive phase ind_brk_start to ind_prop_end

        arr = self.vel_data.value_arr[ind_prop_start : ind_prop_end]

        stats = {'v_peak_prop': arr.max(),
                 'v_peak_neg': self.vel_data.value_arr[ind_unwght_start : ind_brk_end].min(),
                 'v_avg_neg': self.vel_data.value_arr[ind_unwght_start : ind_brk_end].mean(),
                 't_to_v_peak_prop': self.vel_data.time_arr[v_peak_prop_idx] - self.vel_data.time_arr[ind_prop_start],
                 'v_avg_100_prop': self.vel_data.value_arr[ind_prop_start: ind_prop_start + 100].mean(),
                 'a_avg_100_prop': self.acc_data.value_arr[ind_prop_start: ind_prop_start + 100].mean(),
                 'a_peak_100_prop': self.acc_data.value_arr[ind_prop_start: ind_prop_start + 100].max(),
                 'v_peak_100_prop': self.vel_data.value_arr[ind_prop_start: ind_prop_start + 100].max(),
                 'a_peak_pos': self.acc_data.value_arr[ind_brk_start: ind_prop_end].max()
        }

        return stats


    def get_cmj_data_json(self):
        if (self.vel_data.items_count == self.combined_force_data.items_count
            and 
            self.vel_data.items_count == self.acc_data.items_count):
            data_dict = {"Time (s)": self.vel_data.time_arr,
                         "Velocity (m/s)": self.vel_data.value_arr,
                         "Acceleration (m/s^2)": self.acc_data.value_arr,
                         "Left (N)": self.left_force_data.value_arr,
                         "Right (N)": self.right_force_data.value_arr,
                         "Combined (N)": self.combined_force_data.value_arr 
                         }
            df_data = pd.DataFrame(data_dict)
            data_json = df_data.to_dict(orient="records")
            stats_json = self.get_cmj_stats()
            return {"data": data_json, "stats": stats_json}
        else:
            raise ValueError("Arrays have different legnths")



if __name__ == "__main__":
    force_path = r"D:\DevProjects\PythonProjects\athletes_dashboard\data\force\Adam_Lewandowski-10_14_2020.csv"
    vel_path = r"D:\DevProjects\PythonProjects\athletes_dashboard\data\velocity\Adam_Lewandowski-10_14_2020.csv"

    force_csv = CMJJumpForceCSVReader(force_path)
    vel_csv = CMJJumpVelocityCSVReader(vel_path)
    cmj_jump = CMJJumpModel(force_csv.combined_force, vel_csv.velocity, force_csv.left_force, force_csv.right_force)
    pp(cmj_jump.get_cmj_stats())
    


    # cmj_vel_attr = CMJAttribute(rf"{path}\robin\velocity.csv",
    #                             {"time": "Time (s)", "velocity": "Velocity (M/s)"})
    # cmj_force_attr = CMJAttribute(rf"{path}\robin\force.csv",
    #                               {"time": "Time (s)", "left": "Left (N)", "right": "Right (N)",
    #                                "combined": "Combined (N)"})
    # cmj = CMJForceVelStats(cmj_vel_attr, cmj_force_attr, "Time (s)")
    # print("Robin: ")
    # cmj.get_cmj_stats()



"""
STATS FOR CMJ NICE PRINT

v_peak_prop = df_prop["Velocity (M/s)"].max()
v_peak_prop_idx = df_prop["Velocity (M/s)"].idxmax()
v_peak_neg = df_neg_vel["Velocity (M/s)"].min()
v_peak_neg_idx = df_neg_vel["Velocity (M/s)"].idxmin()
v_avg_neg = df_neg_vel["Velocity (M/s)"].mean()
t_to_v_peak_prop = df_prop.loc[v_peak_prop_idx, "Time (s)"] - df_prop.loc[ind_prop_start, "Time (s)"]
v_avg_100_prop = df_prop.loc[ind_prop_start: ind_prop_start + 100, "Velocity (M/s)"].mean()
a_avg_100_prop = df_prop.loc[ind_prop_start: ind_prop_start + 100, "Acceleration (m/s^2)"].mean()
a_peak_100_prop = df_prop.loc[ind_prop_start: ind_prop_start + 100, "Acceleration (m/s^2)"].max()
v_peak_100_prop = df_prop.loc[ind_prop_start: ind_prop_start + 100, "Velocity (M/s)"].max()
a_peak_pos = df_pos_a["Acceleration (m/s^2)"].max()

print("Time to v peak pos:                     {:.4f} s".format(t_to_v_peak_prop))
print("v peak pos:                             {:.4f} m/s".format(v_peak_prop))
print("v peak neg:                             {:.4f} m/s".format(v_peak_neg))
print("v avg 100ms pos:                        {:.4f} m/s".format(v_avg_100_prop))
print("a avg 100ms prop:                       {:.4f} m/s^2".format(a_avg_100_prop))
print("a peak 100ms prop:                      {:.4f} m/s^2".format(a_peak_100_prop))
print("v peak 100ms prop:                      {:.4f} m/s^2".format(v_peak_100_prop))
"""
"""
print("v peak neg /  Time to v peak pos:       {:.4f}".format(v_peak_neg / t_to_v_peak_prop))
print("v peak neg / V peak prop:               {:.4f}".format(v_peak_neg / v_peak_prop))
print("v avg neg / V peak prop:                {:.4f}".format(v_avg_neg / v_peak_prop))
print("v avg neg / first 100 ms v pos avg:     {:.4f} ".format(v_avg_neg / v_avg_100_prop))
print("v peak neg / first 100 ms v pos avg:    {:.4f}".format(v_peak_neg / v_avg_100_prop))
print("v avg neg / first 100 ms acc prop avg:  {:.4f}".format(v_avg_neg / a_avg_100_prop))
print("v peak neg / first 100 ms acc prop avg: {:.4f}".format(v_peak_neg / a_avg_100_prop))
"""

