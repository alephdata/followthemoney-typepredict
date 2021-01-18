import random
from itertools import islice
from pathlib import Path

from followthemoney import model


DEFAULT_FIELDS_LIMIT = {
    "name": 100_000,
    "trash": 100_000,
    "address": 75_000,
    "date": 75_000,
    "email": 75_000,
    "identifier": 75_000,
    "phone": 75_000,
}


class FastTextSampler:
    def __init__(
        self,
        data_path,
        proxy_transformer,
        fields_limit=DEFAULT_FIELDS_LIMIT,
        phase_pct={"train": 0.8, "valid": 0.2},
    ):
        self.data_path = Path(data_path)
        self.fields_limit = fields_limit
        self.proxy_transformer = proxy_transformer
        self.phase_pct = phase_pct
        self._samplers = {
            field: ResevourSampler(limit=limit) for field, limit in fields_limit.items()
        }

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def add_entity(self, entity):
        proxy = model.get_proxy(entity)
        collection_id = proxy.context.get("collection_id")
        for field, sample in self.proxy_transformer(proxy, self.fields_limit):
            self.add(field, sample, collection_id)

    def add(self, field, sample, collection_id=None):
        return self._samplers[field].add(sample, collection_id)

    def full(self):
        return all(s.full() for s in self._samplers.values())

    def close(self):
        fields_labels = {field: f"__label__{field}" for field in self._samplers}
        phase_data = {phase: [] for phase in self.phase_pct}
        phase_sum = sum(self.phase_pct.values())
        for field, sampler in self._samplers.items():
            label = fields_labels[field]
            data = sampler.data_sorted()
            N = len(sampler)
            for phase, pct in self.phase_pct.items():
                M = int(N * (pct / phase_sum))
                phase_data[phase].extend(
                    f"{label} {value}" for value in islice(data, M)
                )
        for phase, lines in phase_data.items():
            random.shuffle(lines)
            fname = self.data_path / f"{phase}.txt"
            fname.parent.mkdir(parents=True, exist_ok=True)
            with open(fname, "w+") as fd:
                for line in lines:
                    fd.write(line)
                    fd.write("\n")

    def __len__(self):
        return sum(len(s) for s in self._samplers.values())

    def __repr__(self):
        members = ", ".join(str(f) for f in self._samplers)
        return f"<FastTextSampler {members}>"


class ResevourSampler:
    def __init__(self, limit):
        self.limit = limit
        self._values = []
        self._dedupe = set()
        self._n_seen = 0

    def data_sorted(self):
        self._values.sort()
        return (value for _, value in self._values)

    def full(self):
        return self.limit <= len(self._values)

    def add(self, value, collection_id=None):
        if not value or value in self._dedupe:
            return False
        self._n_seen += 1
        if len(self) >= self.limit:
            i = random.randint(0, self._n_seen)
            if i < len(self):
                self._dedupe.discard(self.values[i][1])
                self._values[i] = (collection_id, value)
                self._dedupe.add(value)
            return False
        else:
            self._values.append((collection_id, value))
            self._dedupe.add(value)
            return True

    def __len__(self):
        return len(self._values)

    def __str__(self):
        pct = len(self) / self.limit * 100
        return f"{self.type}:{pct:0.0f}%"

    def __repr__(self):
        return f"<ResevourSampler {str(self)}>"
