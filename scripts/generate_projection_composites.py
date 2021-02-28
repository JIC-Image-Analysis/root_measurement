import os
import pathlib
import logging

import click
import pandas as pd

from mruntools.config import Config
from stacktools.data import InitialsSMS, FCARootData
from stacktools.vis import create_file_projection_composite

from generate_spherefit_visualisations import annotated_specs_from_config

logger = logging.getLogger(__file__)


# @click.command()
# @click.argument('image_ds_uri')
# @click.argument('seg_ds_uri')
# @click.argument('root_data_basepath')
# @click.argument('output_basedir')
# @click.option('--root-name', default="fca3_FLCVenus_root2")
# def main(image_ds_uri, seg_ds_uri, root_data_basepath, output_basedir, root_name):
#     logging.basicConfig(level=logging.INFO)
#     logger = logging.getLogger("generate_projection_composites")
#     logging.getLogger("stacktools.cache").setLevel(level=logging.DEBUG)

#     logger.info(f"Loading root {root_name}")
#     loader = FCADataSetLoader(image_ds_uri, seg_ds_uri, root_data_basepath)
#     rootdata = loader.load_root(root_name)

#     for fid in rootdata.files:
#         fsm = create_file_projection_composite(rootdata, fid)
#         fname = f"composite-{root_name}-file{fid}.png"
#         fpath = os.path.join(output_basedir, fname)
#         fsm.save(fpath)


@click.command()
@click.argument('config_fpath')
def main(config_fpath):

    logging.basicConfig(level=logging.INFO)

    config = Config.from_fpath(config_fpath)

    annotated_specs = annotated_specs_from_config(config)
    logger.info(f"Founds specs: {annotated_specs}")

    vis_dirpath = pathlib.Path(config.composite_dirpath)
    vis_dirpath.mkdir(exist_ok=True, parents=True)

    for spec in annotated_specs:
        logger.info(f"Generating image for {spec}")

        sms = InitialsSMS.from_config_and_spec(config, spec)
        root_data = pd.read_csv(config.output_fpath)
        root_data["file_id"] = root_data["label"]

        #FIXME - this isn't quite right
        root_data["cell_centroid"] = root_data["sphere_fit_centroid"]

        selected_root_data = root_data[
            (root_data.root_number == spec.n) &
            (root_data.genotype == spec.genotype)
        ]

        fcaroot = FCARootData(
            spec.image_name,
            sms.wall_stack,
            sms.measure_stack,
            sms.segmentation,
            selected_root_data
        )

        for fid in fcaroot.files:
            fsm = create_file_projection_composite(fcaroot, fid)
            fname = f"{spec.image_name}-file{fid}.png"
            fpath = vis_dirpath/fname

            fsm.save(fpath)


if __name__ == "__main__":
    main()
