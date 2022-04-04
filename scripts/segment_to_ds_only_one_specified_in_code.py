import logging
import pathlib
from types import SimpleNamespace

import click
import dtoolcore

from dtoolbioimage import ImageDataSet, zoom_to_match_scales
from dtoolbioimage.segment import sitk_watershed_segmentation

from stacktools.config import Config


logger  = logging.getLogger("initials")


def process_image_and_series(config, spec, output_ds):

    imageds = ImageDataSet(config.ids_uri)
    wall_stack = imageds.get_stack(
        spec.image_name,
        spec.series_name,
        0,
        config.wall_channel
    )
    logger.info(f"Loaded {spec.series_name} with shape {wall_stack.shape}")
    zoomed_wall_stack = zoom_to_match_scales(wall_stack)
    snfmt = spec.series_name.replace(" ", "_").replace("#", "")

    level = config.params['level']
    logging.info(f"Segmenting with level {level}")
    segmentation = sitk_watershed_segmentation(
        zoomed_wall_stack,
        level=config.params["level"]
    )

    wall_output_relpath = f"{spec.image_name}_{snfmt}_cell_wall.tif"
    seg_output_relpath = f"{spec.image_name}_{snfmt}_segmentation_L{level}.tif"

    wall_output_abspath = output_ds.prepare_staging_abspath_promise(wall_output_relpath)
    seg_output_abspath = output_ds.prepare_staging_abspath_promise(seg_output_relpath)

    segmentation.save(seg_output_abspath)
    zoomed_wall_stack.save(wall_output_abspath)


def stack_tuple_to_spec(stack_tuple):
    names = ["image_name", "series_name", "sidx"]
    tdict = dict(zip(names, stack_tuple))

    return SimpleNamespace(**tdict)


@click.command()
@click.argument('config_fpath')
@click.option('-i','input_name',default=None)
def main(config_fpath, input_name):

    logging.basicConfig(level=logging.INFO)

    config = Config(config_fpath)

    ids = ImageDataSet(config.ids_uri)

    specs = [
        stack_tuple_to_spec(tp)
        for tp in ids.all_possible_stack_tuples()
    ]

    if (input_name is None):
        output_name = config.output_name+'_All'
    else:
        output_name = config.output_name+'_'+input_name
    
    with dtoolcore.DataSetCreator(
        output_name,
        config.output_base_uri
    ) as output_ds:
        logging.info(f"Monitor at: {output_ds.staging_directory}")
        for spec in specs:
            if (input_name is None) or spec.series_name==input_name:
    	        try:
    	            logging.info(f"Processing {spec}")
    	            process_image_and_series(config, spec, output_ds)
    	        except KeyError:
    	            logging.error(f"Failed on {spec}")
                
        readme_str = config.as_readme_format()
        output_ds.put_readme(readme_str)



if __name__ == "__main__":
    main()
