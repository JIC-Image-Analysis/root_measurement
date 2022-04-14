import pathlib

import click
import dtoolcore

from dtoolbioimage.convert import raw_image_dataset_to_image_dataset

from stacktools.config import Config

class IndexedDirtree(object):

    def __init__(self, base_dirpath, glob="*"):
        self.glob = glob
        self.base_dirpath = pathlib.Path(base_dirpath)
        self.index = {
            dtoolcore.utils.generate_identifier(str(rpath)): rpath
            for rpath in self.relpath_iter
        }

    @property
    def abspath_iter(self):
        return (
            fpath
            for fpath in self.base_dirpath.rglob(self.glob)
            if fpath.is_file()
        )

    @property
    def relpath_iter(self):
        return (
            fpath.relative_to(self.base_dirpath)
            for fpath in self.abspath_iter
        )

    @property
    def identifiers(self):
        return list(self.index)

    def item_properties(self, idn):
        rpath = self.index[idn]
        return {
            'relpath': str(rpath)
        }

    def item_content_abspath(self, idn):
        return self.base_dirpath/self.index[idn]

    def __len__(self):
        return len(self.identifiers)


# @click.command()
# @click.argument('data_root_fpath')
def convert_image_data(config):
    # TODO - bfconvert preflight
    glob = config.raw_file_type
    ids = IndexedDirtree(config.raw_data_uri, glob=glob)

    with dtoolcore.DataSetCreator(config.ids_name, config.ids_base_uri) as output_ds:
        raw_image_dataset_to_image_dataset(ids, output_ds)


@click.command()
@click.argument('config_fpath')
def main(config_fpath):

    config = Config(config_fpath)
    
    convert_image_data(config)
    

if __name__ == "__main__":
    main()
