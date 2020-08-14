'''
make.output(tfrecord)(dset_dict, out_path)

If out_path is existing directory, then save file named:
"train-name_revision_size.dev-name_r_s.test-name_r_s.tfrecord"

If name is same(name.{train,dev,test} then file name:
"name.r_s.r_s.r_s.tfrecord"

If out_path is valid and not existing path, 
then file is created with that path.

If out_path is valid but EXISTING path, 
warn to user and stop generation.
'''
from dw.const.types import FileType as FT
from dw.db import schema as S


def valid(dset_dic, out_path):
    # Assume that dataset_dictionary is valid?
    assert out_path.exists()
    return True

def load(dset_dic, out_path):
    return dset_dic, out_path

def generate(loaded):
    return loaded

def canonical(generated):
    dset_dic, out_path = generated
    return [
        S.exported(**dset_dic,
                   type=FT.tfrecord.value,
                   path=str(out_path))
    ], [
    ]
