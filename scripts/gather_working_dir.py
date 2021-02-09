import json
import pathlib

import click
import pandas as pd

from mruntools.config import Config
from mruntools.spec import ItemSpec, item_spec_from_fpath


def get_all_specs(dirpath):

    dirpath = pathlib.Path(dirpath)
    fpath_iter = dirpath.rglob("*.json")
    specs = {
        fpath.stem: item_spec_from_fpath(fpath)
        for fpath in fpath_iter
    }

    return specs


@click.command()
@click.argument("config_fpath")
def main(config_fpath):

    config = Config.from_fpath(config_fpath)
    dirpath = pathlib.Path(config.working_dirpath)

    specs = get_all_specs(dirpath)
    spec_reprs = [spec.__repr__() for spec in specs.values()]

    # Check for duplicates
    assert len(spec_reprs) == len(set(spec_reprs)), "Duplicate spec"

    def load_and_annotate(idn, spec):
        data_fpath = f"{idn}.csv"
        df = pd.read_csv(dirpath/data_fpath, index_col=0)
        df["genotype"] = spec.genotype
        return df

    all_dfs = [load_and_annotate(idn, spec) for idn, spec in specs.items()]
    merged_df = pd.concat(all_dfs)

    merged_df.to_csv(config.output_fpath, index=False, float_format="%.2f")


if __name__ == "__main__":
    main()
