import random
import re
from functools import singledispatch
from itertools import chain

from normality import normalize

from followthemoney import model
from followthemoney.types import registry
from followthemoney.proxy import EntityProxy


DEFAULT_SKIP_SCHEMAS = [model.get("Event"), model.get("Mention")]


def clean_value(value):
    return normalize(value, latinize=True, lowercase=True)


@singledispatch
def transform(_, fields, skip_schemas=DEFAULT_SKIP_SCHEMAS):
    raise ValueError


@transform.register(dict)
def transform_entity(entity, fields, skip_schemas=DEFAULT_SKIP_SCHEMAS):
    proxy = model.get_proxy(entity)
    yield from transform(proxy, fields, skip_schemas=skip_schemas)


@transform.register(EntityProxy)
def transform_proxy(proxy, fields, skip_schemas=DEFAULT_SKIP_SCHEMAS):
    if any(proxy.schema.is_a(s) for s in skip_schemas):
        return
    for field in fields:
        if field == "trash":
            data = generate_trash(proxy)
        else:
            prop = registry.get(field)
            data = proxy.get_type_values(prop)
        yield from ((field, clean_value(value)) for value in data)


def generate_trash(proxy):
    if proxy.schema.is_a(model.get("Page")):
        tokens = chain.from_iterable(
            re.split("\W+", b) for b in proxy.get("bodyText", quiet=True) if b
        )
        tokens = list(filter(None, tokens))
        ngrams = 1
        while random.random() < 0.4:
            ngrams += 1
        n_samples = 1
        while random.random() < 0.6:
            n_samples += 1
        if len(tokens) < ngrams * n_samples:
            return
        for _ in range(n_samples):
            i = random.randint(0, len(tokens) - ngrams)
            sample = tokens[i : i + ngrams]
            if any(len(t) > 1 for t in sample) and all(len(t) < 24 for t in sample):
                yield " ".join(tokens[i : i + ngrams])
