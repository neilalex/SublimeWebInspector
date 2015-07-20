from projectsystem import Sourcemap

class Position:
    def __init__(self, file_name, line, column):
        # zero-based line and column values
        self.__file_name = file_name
        self.__line = line
        self.__column = column

    def one_based_line(self):
        return self.__line + 1

    def one_based_column(self):
        return self.__column + 1

    def zero_based_line(self):
        return self.__line

    def zero_based_column(self):
        return self.__column

    def file_name(self):
        return self.__file_name


class MappingsManager:
    source_file_mappings = {}
    authored_file_mappings = {}

    @staticmethod
    def create_mapping(file_name):
        mapping = MappingInfo(file_name)
        MappingsManager.source_file_mappings[file_name.lower()] = mapping

        authored_files = mapping.get_authored_files()
        for file_name in authored_files:
            MappingsManager.authored_file_mappings[file_name.lower()] = mapping

    @staticmethod
    def is_authored_file(file_name):
        return file_name in MappingsManager.authored_file_mappings

    @staticmethod
    def is_source_file(file_name):
        return file_name in MappingsManager.source_file_mappings

    @staticmethod
    def get_mapping(file_name):
        file_name = file_name.lower()
        if file_name in MappingsManager.source_file_mappings:
            return MappingsManager.source_file_mappings[file_name]

    @staticmethod
    def delete_mapping(file_name):
        file_name = file_name.lower()
        if file_name in MappingsManager.source_file_mappings:
            mapping = MappingsManager.source_file_mappings.pop(file_name)

            # Delete corresponding authored source mappings
            for authored_source in mapping.get_authored_files():
                MappingsManager.authored_file_mappings.pop(authored_source)

    @staticmethod
    def delete_all_mappings():
        MappingsManager.source_file_mappings.clear()
        MappingsManager.authored_file_mappings.clear()


class MappingInfo:
    def __init__(self, generated_file):
        source_map_file = Sourcemap.get_sourcemap_file(generated_file)
        self.parsed_source_map = Sourcemap.ParsedSourceMap(source_map_file)
        self.generated_file = generated_file

        self.authored_sources = []
        if self.parsed_source_map: 
            self.authored_sources = self.parsed_source_map.get_authored_sources_path()
            self.line_mappings = self.parsed_source_map.line_mappings

    def get_authored_files(self):
        return self.authored_sources

    def get_generated_file(self):
        return self.generated_file

    def get_mapped_location(self, zero_based_line, zero_based_column):
        # Invalid line and column values or line mappings do not exist
        if (zero_based_line < 0 or zero_based_column < 0 or len(self.line_mappings) <= 0):
            return None

        mapping_index = Sourcemap.LineMapping.binary_search(self.line_mappings,
                                                            zero_based_line,
                                                            zero_based_column,
                                                            lambda line_mapping, line, column: Sourcemap.LineMapping.compare_generated_mappings(line_mapping, line, column))

        line_number = max(self.line_mappings[mapping_index].source_line, 0)
        column_number = max(self.line_mappings[mapping_index].source_column, 0)
        file_number = max(self.line_mappings[mapping_index].file_num, 0)

        return Position(self.authored_sources[file_number], line_number, column_number)

    def get_generated_location(self, authored_file_name, zero_based_line, zero_based_column):
        return None
