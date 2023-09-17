import os   # for file path iteration and manipulation
import re   # for matching regular expressions patterns in file names

from matter_states_tools.MatterStatesData import MatterStatesData


class VectorPairIdentifier():
    """A class that contains all the data and methods necessary to identify vector pairs and unpaired vectors. Processes all files in a directory, and writes output to files in the same directory.
    """
    def __init__(
            self, 
            data: MatterStatesData, 
            identify: bool = True, 
            write: bool = False
    ):
        self.data = data
        self.directory_path = data.directory
        self.inverse_rms = {}
        self.vector_pairs = {}
        self.unpaired_vectors = []
        self.total_pairs = 0
        self.num_paired_states = 0

        if identify:
            self.create_reverse_rm_dict()
            self.identify_vector_pairs()
        if write:
            self.write_files()

    def create_reverse_rm_dict(self):
        """Inverts the states_rm_dict dictionary, and aggregates states' names.
        """
        self.inverse_rm_dict = {}
        for key, value in self.data.rm_charges.items():
            self.inverse_rms.setdefault(value, []).append(key)

    def identify_vector_pairs(self):
        """Identifies all state pairs that have RM U(1) charges that are additive inverses,and that have matching NA reps. Also identifies states that have no pairs. Total pairs and number of paired states are counted.
        """
        for state_name, rm_charges in self.data.rm_charges.items():
            # Create the target inverse values
            inverse_values = tuple([-1 * c for c in rm_charges])
            # Retrieve all state names that match the inverse values
            matching_states = self.inverse_rms.get(inverse_values, [])

            match_found = False
            for pair_state_name in matching_states:
                if self.data.na_reps[state_name] == self.data.na_reps[pair_state_name]:
                    match_found = True
                    self.total_pairs += 1
                    self.vector_pairs.setdefault(state_name, []).append(pair_state_name)

            if not match_found:
                self.unpaired_vectors.append(state_name)
            else:
                self.num_paired_states += 1

    def write_files(self):
        """Writes the vector pairs and unpaired vectors to their respective output files.
        """
        self.write_vector_pairs_file(self.data.tower_name)
        self.write_unpaired_vectors_file(self.data.tower_name)

    def write_vector_pairs_file(self, tower_name: str):
        """Writes the vector pairs to their respective output file.

        Args:
            tower_name (str): The name of the tower (e.g. '2Ms1.EL0.ER1.')
        """
        file_path = os.path.join(self.directory_path, self.data.tower_name) + "vector_pairs.txt"
        with open(file_path, 'w') as write_file:
            for state, pairs in self.vector_pairs.items():
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
