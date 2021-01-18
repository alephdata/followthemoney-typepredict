from pprint import pprint
import fasttext

try:
    import seaborn as sn
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.metrics import confusion_matrix

    ANALYSIS_MODULES = True
except ImportError:
    ANALYSIS_MODULES = False


class Model:
    def __init__(self, model=None):
        self.model = model

    def save(self, path):
        self.model.save_model(str(path))

    @classmethod
    def load(cls, path):
        return cls(model=fasttext.load_model(str(path)))

    def fit(self, *, tune, train, valid, quantize, tune_durration=600):
        print("Training type model with the following parameters:")
        print(f"\tTune: {tune}")
        print(f"\tTrain: {train}")
        print(f"\tValid: {valid}")
        print(f"\tQuantize: {quantize}")
        print(f"\tTune Durration: {tune_durration}")
        self.model = fasttext.train_supervised(
            input=str(train),
            autotuneValidationFile=str(tune),
            autotuneDuration=tune_durration,
        )
        print("Quantizing model")
        self.model.quantize(verbose=True, input=str(quantize), retrain=True)
        results = self.evaluate(valid)
        print("Fitting done. Model evaluation:")
        pprint(results)
        return results

    def predict(self, data, k=-1):
        result = list(zip(*self.model.predict(data, k=k)))
        return result

    def evaluate(self, data):
        if self.model is None:
            raise ValueError("Cannot evaluate untrained model")
        return self.model.test_label(str(data))

    def plot(self, data):
        if not ANALYSIS_MODULES:
            raise ImportError("Analysis modules not installed")
        elif self.model is None:
            raise ValueError("Cannot plot untrained model")
        y_X = [list(map(str.strip, line.split(" ", 1))) for line in open(data)]
        y, X = zip(*y_X)
        y = list(y)
        X = list(X)
        labels = self.model.get_labels()
        labels_pretty = [label.replace("__label__", "") for label in labels]
        y_pred = self.model.predict(X)[0]
        cm = confusion_matrix(y, y_pred, labels=labels, normalize="true")
        df_cm = pd.DataFrame(cm, index=labels_pretty, columns=labels_pretty)
        plt.figure(figsize=(15, 10))
        plt.clf()
        sn.heatmap(df_cm, annot=True, fmt=".2f")
        plt.title("Confusion Matrix")
        plt.ylabel("actual")
        plt.xlabel("predict")
        plt.tight_layout()
        return plt.gcf()
