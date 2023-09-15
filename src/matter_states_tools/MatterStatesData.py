import os
import re


class MatterStatesData():
    def __init__(
            self, 
            directory: str, 
            dc_format: bool = False, 
            dont_load: bool = False
    ):
        self.directory = directory
        self.fmm = {}
        self.lm_charges = {}
        self.rm_charges = {}
        self.na_reps = {}
        self.dc_format = dc_format
        self.states = None  # [[0]*64] * self.num_states

        if not dont_load:
            self.load_lms()
            self.load_rms()
            self.load_nas()

    def load_lms(self):
        """Loads the LM data from the file into its respective dictionary.

        Args:
            file_path (str): The path to the file containing the LM data.
        """
        files_in_dir = os.listdir(self.directory)
        for file in files_in_dir:
            full_path = os.path.join(self.directory, file)
            if os.path.isfile(full_path) and file.endswith(".lm.u1.all"):
                file_path = full_path
                break

        with open(file_path, 'r', encoding="utf-8") as lm_readfile:
            lines = lm_readfile.readlines()
            for line in lines:
                if self.dc_format:
                    name_pattern = r"\((\s*\d+.){3} [\w\?\s]{4}"
                    state_name = re.search(name_pattern, line)
                    if not state_name:
                        continue
                    state_name = state_name.group()
                    
                    charges = re.findall(r'-?\d\.\d{2}', line)
                    lm_u1s = list(map(float, charges))
                else:
                    state_name = re.search(r'\w+', line)
                    if not state_name:
                        continue
                    state_name = state_name.group()
                    charges = re.findall(r'-?\d\.\d{2}', line)
                    lm_u1s = list(map(float, charges))
                    
                if not state_name or not lm_u1s:
                    continue
                if not self.dc_format:
                    try:  # because the VEVs are sort of weird 
                        pop_indecies = (17, 15, 13, 11, 9, 7)
                        for i in pop_indecies:
                            del lm_u1s[i]
                    except IndexError:
                        pass

                self.lm_charges[state_name] = tuple(lm_u1s)

    def load_rms(self):
        """Loads the RM data from the file into the dictionary.

        Args:
            file_path (str): The path to the file containing the RM data.
        """
        files_in_dir = os.listdir(self.directory)
        for file in files_in_dir:
            full_path = os.path.join(self.directory, file)
            if os.path.isfile(full_path) and file.endswith(".rm.u1.all"):
                file_path = full_path
                break

        with open(file_path, 'r', encoding="utf-8") as rm_readfile:
            lines = rm_readfile.readlines()

            for line in lines:
                if self.dc_format:
                    name_pattern = r"\((\s*\d+.){3} [\w\?\s]{4}"
                    state_name = re.search(name_pattern, line)
                    if not state_name:
                        continue
                    state_name = state_name.group()
                    
                    line_charges = re.split(re.escape(state_name), line)
                    charge_pattern = r"\s+(-?\d+)"
                    found_reps = re.findall(charge_pattern, line_charges[1])
                    if not found_reps:
                        continue
                    charges = [int(r) for r in found_reps]
                else:
                    state_name = re.search(r'\w+', line)
                    if not state_name:
                        continue
                    state_name = state_name.group()

                    found_reps = re.findall(r'\s+(-?\d+)', line)
                    if not found_reps:
                        continue
                    charges = list(map(int, found_reps))
                
                if len(charges) < 12:
                    continue
                self.rm_charges[state_name] = charges

    def load_nas(self):
        """Loads the NA data from the file into the dictionary.

        Args:
            file_path (str): The path to the file containing the NA data.
        """
        files_in_dir = os.listdir(self.directory)
        for file in files_in_dir:
            full_path = os.path.join(self.directory, file)
            if os.path.isfile(full_path) and file.endswith(".rm.na.all"):
                file_path = full_path
                break

        with open(file_path, 'r', encoding="utf-8") as na_readfile:
            lines = na_readfile.readlines()
            for line in lines:
                if self.dc_format:
                    name_pattern = r"\((\s*\d+.){3} [\w\?\s]{4}"
                    state_name = re.search(name_pattern, line)
                    if not state_name:
                        continue
                    state_name = state_name.group()
                    
                    reps_pattern = r"[\w\?\s]{4}\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)"
                    found_reps = re.search(reps_pattern, line)
                    if not found_reps:
                        continue
                    reps = [int(r) for r in found_reps.groups()]
                else:
                    state_name = re.search(r'\w+', line)
                    if not state_name:
                        continue
                    state_name = state_name.group()

                    found_reps = re.findall(r'\s+(-?\d+)', line)
                    if not found_reps:
                        continue
                    reps = list(map(int, found_reps))

                # if len(reps) != 5:
                #     continue

                for i, r in enumerate(reps):
                    if r % 3 == 0 and r < 0:
                        reps[i] = -1 * r
                    else:
                        reps[i] = r
                
                if self.dc_format:
                    temp = list(reps)
                    reps[0] = temp[3]
                    reps[1] = temp[4]
                    reps[2] = temp[1]
                    reps[3] = temp[2]
                    reps[4] = temp[0]

                self.na_reps[state_name] = tuple(reps)
