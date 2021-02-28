import os
import click
import logging
import pathlib

import numpy as np
import pandas as pd

from dtoolbioimage import ImageDataSet, Image as dbiImage
from mruntools.config import Config
from mruntools.spec import specs_from_fpath_metadata
from stacktools.data import InitialsSMS, FCARootData
from stacktools.vis import create_annotated_file_projection


logger = logging.getLogger(__file__)


def generate_candidate_item_specs(config):

    return specs_from_fpath_metadata(
        config.segmentation_dirpath,
        config.parse_templates
    )


def annotated_specs_from_config(config):

    specs = generate_candidate_item_specs(config)

    ids = ImageDataSet(config.ids_uri)

    try:
        sidx = config.specifier_tuple_index
    except KeyError:
        sidx = 0

    tuple_lookup = {
        st[sidx]: st
        for st in ids.all_possible_stack_tuples()
    }

    def annotate_spec(spec):
        spec_template = config.segmentation_spec_template
        spec_key = spec.template_repr(spec_template)
        spec.image_name, spec.series_name, spec.sidx = tuple_lookup[spec_key]
        spec.fname = spec.template_repr(config.segmentation_fname_template)
        spec.regions_fname = spec.template_repr(config.regions_fname_template)

        return spec

    annotated_specs = [annotate_spec(spec) for spec in specs]

    return annotated_specs


@click.command()
@click.argument('config_fpath')
def main(config_fpath):

    logging.basicConfig(level=logging.INFO)

    config = Config.from_fpath(config_fpath)

    try:
        sidx = config.specifier_tuple_index
    except KeyError:
        sidx = 0
    
    annotated_specs = annotated_specs_from_config(config)
    logger.info(f"Founds specs: {annotated_specs}")

    vis_dirpath = pathlib.Path(config.visualisation_dirpath)
    vis_dirpath.mkdir(exist_ok=True, parents=True)

    for spec in annotated_specs:
        logger.info(f"Generating image for {spec}")

        sms = InitialsSMS.from_config_and_spec(config, spec)
        root_data = pd.read_csv(config.output_fpath)
        root_data["file_id"] = root_data["label"]

        try:
            testIfSn = spec.n
        except AttributeError:
            spec.n = 1
            
        selected_root_data = root_data[
            (root_data.root_number == spec.n) & \
            (root_data.genotype == spec.genotype)
        ]

        fcaroot = FCARootData(
            spec.image_name,
            sms.wall_stack,
            sms.measure_stack,
            sms.segmentation,
            selected_root_data
        )

        # fid = 3
        # p = create_annotated_file_projection(fcaroot, fid, fcaroot.denoised_venus_stack)
        # p.view(dbiImage).save("p.png")


        sections = [
            create_annotated_file_projection(fcaroot, fid, fcaroot.denoised_venus_stack)
            for fid in fcaroot.files
        ]

        if sidx>0:
            output_fpath = vis_dirpath/f"{spec.series_name}.png"
        else:
            output_fpath = vis_dirpath/f"{spec.image_name}.png"
        
        composite = np.vstack(sections).view(dbiImage)
        composite.save(output_fpath)




if __name__ == "__main__":
    main()
