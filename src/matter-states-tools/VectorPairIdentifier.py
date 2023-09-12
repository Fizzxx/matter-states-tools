import os   # for file path iteration and manipulation
import re   # for matching regular expressions patterns in file names


class VectorPairIdentifier():
    """A class that contains all the data and methods necessary to identify vector pairs and unpaired vectors. Processes all files in a directory, and writes output to files in the same directory.
    """
    def __init__(self, directory_path: str = None):
        self.directory_path = directory_path
        self.rm_charge_dict = {}
        self.na_reps_dict = {}
        self.inverse_rm_dict = {}
        self.vector_pair_dict = {}
        self.total_pairs = 0
        self.num_paired_states = 0
        self.unpaired_vectors = []

    def create_rm_charge_dictionary(self, file_stem: str):
        """Collects all state names and respective RM U(1) charges into a dictionary.

        Args:
            file_stem (str): The path stem of the filename, which identifies the tower. (e.g. '2Ms1.EL0.ER1.')

        Returns:
            dict: A dictionary where keys are the state identifiers and values 
                    are lists of charges as integers.
        """
        self.rm_charge_dict = {}

        file_path = os.path.join(self.directory_path, file_stem) + "rm.u1.all"
        with open(file_path, 'r', encoding="utf-8") as rmu1_readfile:
            lines = rmu1_readfile.readlines()

            for line in lines:
                line_split = line.split('\t\t ')

                state_name = line_split[0]
                curr_state_rm = line_split[1].strip()

                curr_state_rm_split = curr_state_rm.split('\t ')
                curr_state_rm_charges = tuple(int(x) for x in curr_state_rm_split)

                self.rm_charge_dict[state_name] = curr_state_rm_charges
        self.create_reverse_rm_dict()

    def create_na_reps_dictionary(self, file_stem: str):
        """Collects all the state names and respective NA representations into a dictionary.

        Args:
            file_stem (str): The path stem of the filename, which identifies the tower. (e.g. '2Ms1.EL0.ER1.')

        Returns:
            dict: A dictionary where keys are the state identifiers and values are single lists of reps as integers.
        """
        self.na_reps_dict = {}
        file_path = os.path.join(self.directory_path, file_stem) + "rm.na.all"
        with open(file_path, 'r', encoding="utf-8") as rmna_readfile:
            lines = rmna_readfile.readlines()

            for line in lines:
                line_split = line.split('\t\t')

                state_name = line_split[0]
                curr_state_na = []
                valid_reps = True
                for x in line_split[1].split(' \t')[:-1]:
                    try:
                        x = int(x.strip())
                    except ValueError:
                        valid_reps = False
                        break

                    # If a rep dimension is a multiple of 3,
                    #   it's barred rep is treated as equivalent.
                    if x % 3 == 0 and x < 0:
                        curr_state_na.append(-1 * x)
                    else:
                        curr_state_na.append(x)
                if valid_reps:
                    self.na_reps_dict[state_name] = curr_state_na

    def create_reverse_rm_dict(self):
        """Inverts the states_rm_dict dictionary, and aggregates states' names.
        """
        self.inverse_rm_dict = {}
        for key, value in self.rm_charge_dict.items():
            self.inverse_rm_dict.setdefault(value, []).append(key)

    @staticmethod
    def extract_tower_name(file_name: str):
        """Reads an input file name, and identifies the descriptor for the tower it belongs to.

        Args:
            file_name (str): The name of the file

        Returns:
            str: the stem of the file name which identifies the tower.
        """
        input_file_pattern = r'2Ms[0-9]+\.EL[0-9]\.ER[0-9]\.[lr]m\.[un][1a]\.all'
        tower_name_pattern = r'2Ms[0-9]+\.EL[0-9]\.ER[0-9]\.'

        if not re.match(input_file_pattern, file_name):
            return None

        return re.search(tower_name_pattern, file_name).group()

    def build_pair_dictionaries(self):
        """Identifies all state pairs that have RM U(1) charges that are additive inverses,and that have matching NA reps. Also identifies states that have no pairs. Total pairs and number of paired states are counted.

        Args:
            rm_charges (dict): A dictionary where keys are the state identifiers and values 
                                are lists of charges as integers.
            na_reps (dict): A dictionary where keys are the state identifiers and values are 
                                lists of reps as integers.
            inverse_rm (dict): The inverted dictionary, where keys are the RM U(1) charges 
                                and values are lists of all state names matching those charges.

        Returns:
            tuple: A tuple containing the following:
                dict: A dictionary where keys are the state identifiers and values are lists 
                        of state names that are paired with the key state.
                int: The total number of pairs identified.
                int: The number of states that have pairs.
                list: A list of state names that have no pairs.
        """
        # resets counts to avoid double counting
        self.total_pairs = 0
        self.num_paired_states = 0
        self.vector_pair_dict = {}
        self.unpaired_vectors = []


        for state_name, rm_charges in self.rm_charge_dict.items():
            # Create the target inverse values
            inverse_values = tuple([-1 * c for c in rm_charges])
            # Retrieve all state names that match the inverse values
            matching_states = self.inverse_rm_dict.get(inverse_values, [])

            match_found = False
            for pair_state_name in matching_states:
                if self.na_reps_dict[state_name] == self.na_reps_dict[pair_state_name]:
                    match_found = True
                    self.total_pairs += 1
                    self.vector_pair_dict.setdefault(state_name, []).append(pair_state_name)

            if not match_found:
                self.unpaired_vectors.append(state_name)
            else:
                self.num_paired_states += 1

    def identify_vector_pairs(self):
        """Takes a directory containing matter state output files, and identifies all state pairs and any states that are unpaired. Output is written to a file in the same directory.

        Args:
            directory (str): The path to the directory containing the matter state output files.
        """
        prev_tower_name = ''

        for item in os.listdir(self.directory_path):
            if not os.path.isfile(os.path.join(self.directory_path, item)):
                continue

            tower_name = self.extract_tower_name(item)

            # We only want to process each tower once
            if not tower_name or tower_name == prev_tower_name:
                continue
            prev_tower_name = tower_name

            self.create_rm_charge_dictionary(tower_name)
            self.create_na_reps_dictionary(tower_name)

            self.build_pair_dictionaries()

            self.write_vector_pairs_file(tower_name)
            self.write_unpaired_vectors_file(tower_name)

    def write_vector_pairs_file(self, tower_name: str):
        """Writes the vector pairs to their respective output file.

        Args:
            tower_name (str): The name of the tower (e.g. '2Ms1.EL0.ER1.')
        """
        file_path = os.path.join(self.directory_path, tower_name) + "vector_pairs.txt"
        with open(file_path, 'w') as write_file:
            for state, pairs in self.vector_pair_dict.items():
                write_file.write(f'{state}:')
                for pair in pairs:
                    write_file.write(f'{pair} ')
                write_file.write('\n')
            write_file.write(f'\nTotal number of pairs: {self.total_pairs}')
            write_file.write(f'\nNumber of paired states: {self.num_paired_states}')

    def write_unpaired_vectors_file(self, tower_name: str):
        """Writes the unpaired vectors to their respective output file.

        Args:
            tower_name (str): The name of the tower (e.g. '2Ms1.EL0.ER1.')
        """
        file_path = os.path.join(self.directory_path, tower_name) + "up_vectors.txt"
        with open(file_path, 'w') as write_file:
            for state in self.unpaired_vectors:
                write_file.write(f'{state}\n')
            write_file.write(
                f'\nTotal number of unpaired states: {len(self.unpaired_vectors)}'
            )


if __name__ == '__main__':
    data_directory = r'./2Ms1.EL0.ER0/'
    vp_identifier = VectorPairIdentifier(data_directory)
    vp_identifier.identify_vector_pairs()
