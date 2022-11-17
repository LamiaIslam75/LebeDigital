import os
from pathlib import Path
from doit import create_after
from doit.task import clean_targets

from lebedigital.raw_data_processing.youngs_modulus_data \
    .emodul_metadata_extraction import emodul_metadata

from lebedigital.mapping.emodul_mapping import generate_knowledge_graph

from lebedigital.raw_data_processing.youngs_modulus_data \
    .emodul_generate_processed_data import processed_data_from_rawdata

from lebedigital.openbis.expstep import upload_to_openbis_doit

from doit import get_var

# set a variable to define a cheap or full run
# the default "doit" is set to "doit mode=cheap"
# any other mode value runs the expensive version i.e. "doit mode=full"
config = {"mode": get_var('mode', 'cheap')}

DOIT_CONFIG = {'verbosity': 2}

# openbis config needed for the upload to the datastore
openbis_config = {
    'datastore_url': 'https://test.datastore.bam.de/openbis/',
    'space': 'CKUJATH',
    'project': 'LEBEDIGITAL',
    'collection': 'LEBEDIGITAL_COLLECTION',
    'sample_code': 'EXPERIMENTAL_STEP_EMODUL',
    'sample_prefix': 'EMODUL',
    # 'verbose': True,
    # if actions is specified the task will be completed but the openbis connection will be skipped
    # we need to skip the openbis functions on github actions as they need a password to run
    'runson': get_var('runson', 'actions'),
}

# parent directory of the minimum working example
ParentDir = os.path.dirname(Path(__file__))

# defining paths
emodul_output_directory = Path(ParentDir, 'emodul')  # folder with metadata yaml files
raw_data_emodulus_directory = Path(ParentDir, 'Data', 'E-modul')  # folder with folders of raw data files
metadata_emodulus_directory = Path(emodul_output_directory, 'metadata_yaml_files')  # folder with metadata yaml files
processed_data_emodulus_directory = Path(emodul_output_directory, 'processed_data')  # folder with csv data files
knowledge_graphs_directory = Path(emodul_output_directory, 'knowledge_graphs')  # folder with KG ttl files
openbis_samples_directory = Path(emodul_output_directory, 'openbis_samples')  # folder with openbis log outputs

# when "cheap option" is run, only this souce of raw data is processed
cheap_example_name = 'Wolf 8.2 Probe 1'

# create folder, if it is not there
Path(emodul_output_directory).mkdir(parents=True, exist_ok=True)

# extract standardized meta data for Young' modulus tests


def task_extract_metadata_emodul():
    # create folder, if it is not there
    Path(metadata_emodulus_directory).mkdir(parents=True, exist_ok=True)

    # setting for fast test, defining the list
    if config['mode'] == 'cheap':
        list_raw_data_emodulus_directories = [
            Path(raw_data_emodulus_directory, cheap_example_name)]
    else:  # go through all files
        list_raw_data_emodulus_directories = os.scandir(
            raw_data_emodulus_directory)

    for f in list_raw_data_emodulus_directories:
        if f.is_dir():
            raw_data_path = Path(f)
            raw_data_file = Path(f, 'specimen.dat')
            yaml_metadata_file = Path(
                metadata_emodulus_directory, f.name + '.yaml')
            yield {
                'name': yaml_metadata_file,
                'actions': [(emodul_metadata, [raw_data_path, yaml_metadata_file])],
                'file_dep': [raw_data_file],
                'targets': [yaml_metadata_file],
                'clean': [clean_targets]
            }

# extract standardized processed data for Young' modulus tests


def task_extract_processed_data_emodul():
    # create folder, if it is not there
    Path(processed_data_emodulus_directory).mkdir(parents=True, exist_ok=True)

    # setting for fast test, defining the list
    if config['mode'] == 'cheap':
        list_raw_data_emodulus_directories = [
            Path(raw_data_emodulus_directory, cheap_example_name)]
    else:  # go through all files
        list_raw_data_emodulus_directories = os.scandir(
            raw_data_emodulus_directory)

    for f in list_raw_data_emodulus_directories:
        if f.is_dir():
            raw_data_file = Path(f, 'specimen.dat')
            # the name of the csv file is the file name of the raw data
            # is processed_data_directory + directory_raw_data.csv
            csv_data_file = Path(
                processed_data_emodulus_directory, f.name + '.csv')

            yield {
                'name': csv_data_file,
                'actions': [(processed_data_from_rawdata, [f, csv_data_file])],
                'file_dep': [raw_data_file],
                'targets': [csv_data_file],
                'clean': [clean_targets]
            }


# generate knowledgeGraphs
@create_after(executed='extract_metadata_emodul')
def task_export_knowledgeGraph_emodul():
    # create folder, if it is not there
    Path(knowledge_graphs_directory).mkdir(parents=True, exist_ok=True)

    # setting for fast test, defining the list
    if config['mode'] == 'cheap':
        list_metadata_yaml_files = [
            Path(metadata_emodulus_directory, cheap_example_name + '.yaml')]
    else:  # go through all files
        # list of all meta data files....
        list_metadata_yaml_files = os.scandir(metadata_emodulus_directory)

    # check directory, if

    for f in list_metadata_yaml_files:
        if f.is_file():
            # path to metadata yaml
            metadata_file_path = Path(f)
            name_of_ttl = f.name.replace('.yaml', '.ttl')
            name_of_cvs = f.name.replace('.yaml', '.csv')
            # path the processed data csv
            processed_data_file_path = Path(
                processed_data_emodulus_directory, name_of_cvs)
            # path to output file KG
            knowledge_graph_file = Path(
                knowledge_graphs_directory, name_of_ttl)

            yield {
                'name': knowledge_graph_file,
                'actions': [(generate_knowledge_graph, [metadata_file_path,
                                                        knowledge_graph_file])],
                'file_dep': [metadata_file_path, processed_data_file_path],
                'targets': [knowledge_graph_file],
                'clean': [clean_targets]
            }


@create_after(target_regex='.*emodul$')
def task_upload_to_openbis():
    # create folder, if it is not there
    Path(openbis_samples_directory).mkdir(parents=True, exist_ok=True)

    metadata_directory_path = Path(metadata_emodulus_directory)
    processed_directory_path = Path(processed_data_emodulus_directory)

    # TODO: FIND OUT IF ZIP WILL KEEP THE ORDER OF THE DIRECTORY IN ODER WITH >1 FILE
    for meta_f, processed_f in zip(os.scandir(metadata_emodulus_directory), os.scandir(processed_data_emodulus_directory)):

        # getting path for files
        metadata_file_path = Path(meta_f)
        processed_file_path = Path(processed_f)

        # the raw data file is the specimen file in the corresponding folder in raw_data_emodulus_directory
        raw_data_file = Path(
            raw_data_emodulus_directory, os.path.splitext(os.path.basename(meta_f))[0], 'specimen.dat')

        sample_file_name = os.path.basename(metadata_file_path)
        sample_file_path = Path(openbis_samples_directory, sample_file_name)

        yield {
            'name': metadata_file_path,
            'actions': [(upload_to_openbis_doit, [metadata_file_path, processed_file_path, raw_data_file, openbis_samples_directory, openbis_config])],
            'file_dep': [metadata_file_path, processed_file_path],
            'targets': [sample_file_path],
            'clean': [clean_targets],
        }
