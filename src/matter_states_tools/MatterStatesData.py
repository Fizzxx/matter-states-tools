import os
import re


class MatterStatesData():
    def __init__(
            self, 
            directory: str, 
            dc_format: bool = False, 
            load: bool = True
    ):
        self.directory = directory
        self.lm_charges = {}
        self.rm_charges = {}
        self.na_reps = {}
        self.dc_format = dc_format
        self.tower_name = None
        self.states = None  # [[0]*64] * self.num_states

        if load:
            self.load_all()
            self.tower_name = self.identify_tower()

    def find_file(self, file_class: str):
        """Finds the file of the given class in the directory.

        Args:
            file_class (str): The class of file, represented by the latter half of the 
                    filename. (e.g. '.lm.u1.all', '.rm.na.all', etc.)
        """
        files_in_dir = os.listdir(self.directory)
        for file in files_in_dir:
            full_path = os.path.join(self.directory, file)
            if os.path.isfile(full_path) and file.endswith(file_class):
                return full_path
            
    def identify_tower(self):
        """Identifies the tower name from the files in the directory.
        """
        tower_name_pattern = r"2Ms\d+\.EL\d+\.ER\d+\."
        for item in os.listdir(self.directory):
            tower_name = re.search(tower_name_pattern, item)
            if tower_name:
                return tower_name.group()

    def load_all(self):
        """Loads all of the data from the files into their respective dictionaries.
        """
        self.load_lms()
        self.load_rms()
        self.load_nas()

    def load_lms(self):
        """Loads the LM data from the file into its respective dictionary.
        """
        if self.dc_format:
            name_pattern = r"\((\s*\d+.){3} [\w\?\s]{4}"
            charge_pattern = r"\s+(-?\d\.\d{2})\s"
        else:
            name_pattern = r'\w+'
            charge_pattern = r"\s+(-?\d\.\d{2})"

        file_path = self.find_file(".lm.u1.all")
        with open(file_path, 'r', encoding="utf-8") as lm_readfile:
            lines = lm_readfile.readlines()
            for line in lines:
                state_name = re.search(name_pattern, line)
                if not state_name:
                    continue
                state_name = state_name.group()

                lm_charges = re.findall(charge_pattern, line)
                lm_charges = list(map(float, lm_charges))
                    
                if not self.dc_format:
                    try:  # <- because the VEVs format is sort of weird 
                        pop_indecies = (17, 15, 13, 11, 9, 7)
                        for i in pop_indecies:
                            del lm_charges[i]
                    except IndexError:
                        pass

                self.lm_charges[state_name] = tuple(lm_charges)

    def load_rms(self):
        """Loads the RM data from the file into the respective dictionary.
        """
        if self.dc_format:
            name_pattern = r"\((\s*\d+.){3} [\w\?\s]{4}"
            charge_pattern = r"\s+(-?\d+)\s"
        else:
            name_pattern = r'\w+'
            charge_pattern = r"\s+(-?\d+)"

        file_path = self.find_file(".rm.u1.all")
        with open(file_path, 'r', encoding="utf-8") as rm_readfile:
            lines = rm_readfile.readlines()

            for line in lines:
                state_name = re.search(name_pattern, line)
                if not state_name:
                    continue
                state_name = state_name.group()

                rm_charges = re.findall(charge_pattern, line)
                rm_charges = tuple(map(int, rm_charges))
                if len(rm_charges) != 12:
                    print(len(rm_charges))
                    continue

                self.rm_charges[state_name] = rm_charges

    def load_nas(self):
        """Loads the NA data from the file into the respective dictionary.
        """
        if self.dc_format:
            name_pattern = r"\((\s*\d+.){3} [\w\?\s]{4}"
            reps_pattern = r"[\w\?\s]{4}\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)"
            find_reps = lambda x : [int(r) for r in re.search(reps_pattern, x).groups()]
        else:
            name_pattern = r'\w+'
            reps_pattern = r'\s+(-?\d+)'
            find_reps = lambda x : list(map(int, re.findall(reps_pattern, x)))

        file_path = self.find_file(".rm.na.all")
        with open(file_path, 'r', encoding="utf-8") as na_readfile:
            lines = na_readfile.readlines()
            for line in lines:
                state_name = re.search(name_pattern, line)
                if not state_name:
                    continue
                state_name = state_name.group()
                reps = find_reps(line)

                if not reps:
                    continue

                # Groups are in a different order in Dr. Cleaver's data
                if self.dc_format:
                    temp = list(reps)
                    reps[0] = temp[3]
                    reps[1] = temp[4]
                    reps[2] = temp[1]
                    reps[3] = temp[2]
                    reps[4] = temp[0]

                self.na_reps[state_name] = tuple(reps)
