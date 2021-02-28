import logging
import pathlib

import click
import parse
import pandas as pd

from dtoolbioimage import ImageDataSet
from dtoolbioimage.segment import Segmentation3D
from mruntools.config import Config
from mruntools.run import run_process
from mruntools.spec import specs_from_fpath_metadata, get_all_specs
from stacktools.data import InitialsSMS
from stacktools.data import SegmentationMeasureStack
from stacktools.measure import measure_all_regions


logger = logging.getLogger(__file__)


def generate_candidate_item_specs(config):

    return specs_from_fpath_metadata(
        config.segmentation_dirpath,
        config.parse_templates
    )


@click.command()
@click.argument('config_fpath')
def main(config_fpath):

    logging.basicConfig(level=logging.INFO)

    config = Config.from_fpath(config_fpath)

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
    completed_specs = get_all_specs(config.working_dirpath)

    remaining_specs = set(annotated_specs) - set(completed_specs)
    logging.info(f"Completed {len(completed_specs)}, {len(remaining_specs)} left")

    def measure_from_spec(spec):
        sms = InitialsSMS.from_config_and_spec(config, spec)
        measures = measure_all_regions(sms)
        try:
            measures['root_number'] = spec.n
        except AttributeError:
            measures['root_number'] = 1

        return measures

    selected_specs = remaining_specs
    all_measures = run_process(selected_specs, measure_from_spec, config)




if __name__ == "__main__":
    main()
