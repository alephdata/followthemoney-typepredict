from pathlib import Path
from os import path
from pprint import pprint

import click
import orjson

from .model import Model
from .sampler import FastTextSampler
from .transform import transform, clean_value


DEFAULT = object()


def check_file(fname, default=DEFAULT):
    if not path.exists(fname):
        if default is not DEFAULT:
            return default
        raise FileNotFoundError(fname)
    return fname


@click.group()
def cli():
    pass


@cli.command("create-training-data")
@click.argument("input-data-files", nargs=-1, type=click.File("r"))
@click.argument("output-dir", type=click.Path(file_okay=False, writable=True))
def create_training_data(input_data_files, output_dir):
    """
    Given data files from `aleph sample-entities`, this command will output
    training files for the model.
    """
    with FastTextSampler(output_dir, proxy_transformer=transform) as sampler:
        for input_data_file in input_data_files:
            for line in input_data_file:
                data = orjson.loads(line)
                sampler.add_entity(data)


@cli.command("train-model")
@click.argument(
    "model-file", type=click.Path(dir_okay=False, exists=False), required=True
)
@click.option("--data-dir", type=click.Path(readable=True, exists=True))
@click.option("--tune", type=click.Path(dir_okay=False, exists=True))
@click.option("--train", type=click.Path(dir_okay=False, exists=True))
@click.option("--valid", type=click.Path(dir_okay=False, exists=True))
@click.option("--quantize", type=click.Path(dir_okay=False, exists=True))
@click.option("--tune-durration", type=int, default=600)
def train_model(data_dir, model_file, tune, train, valid, quantize, tune_durration):
    """
    Train a model given the prepared data. If data-dir is provided, we look for the following files:
        train.txt
        valid.txt
        quantize.txt (defaults to train.txt)
        tune.txt (defaults to valid.txt)
    These files can also be provided individually. The files are used for:
        tune.txt - Data to tune model parameters
        train.txt - Base training data for the model
        valid.txt - Model Evaluation
        quantize.txt - Data to refit model with durring quantization
    """
    has_files = bool(tune and train and valid and quantize)
    if not bool(data_dir) ^ has_files:
        raise ValueError("Must supply one of: data_dir OR individual files")
    elif data_dir:
        data_dir = Path(data_dir)
        train = check_file(data_dir / "train.txt")
        valid = check_file(data_dir / "valid.txt")
        quantize = check_file(data_dir / "quantize.txt", train)
        tune = check_file(data_dir / "tune.txt", valid)

    model = Model()
    results = model.fit(
        tune=tune,
        train=train,
        valid=valid,
        quantize=quantize,
        tune_durration=tune_durration,
    )
    model.save(model_file)


@cli.command("evaluate-model")
@click.argument(
    "model-file", type=click.Path(dir_okay=False, exists=True), required=True
)
@click.argument(
    "data-file", type=click.Path(dir_okay=False, exists=True), required=True
)
@click.option("--results-file", type=click.File("wb"), default="-")
@click.option("--plot", type=click.Path(dir_okay=False), default="./evaluate-model.png")
def evaluate_model(model_file, data_file, results_file, plot):
    model = Model.load(model_file)
    results = model.evaluate(data_file)
    if results_file.name == "<stdout>":
        pprint(results)
    else:
        results_file.write(orjson.dumps(results))
    if plot:
        try:
            fig = model.plot(data_file)
            fig.savefig(plot, dpi=300)
        except ImportError as e:
            click.echo(f"Couldn't plot model: {e}")


@cli.command("test-model")
@click.argument(
    "model-file", type=click.Path(dir_okay=False, exists=True), required=True
)
@click.argument("data-file", type=click.File("r"), default="-")
@click.option("--n-labels", type=int, default=-1)
def test_model(model_file, data_file, n_labels):
    model = Model.load(model_file)
    for line in data_file:
        value = clean_value(line)
        pprint(model.predict(value, k=n_labels))
