import numpy as np
import matplotlib.pyplot as plt

class LinearRegressionGd:
    def __init__(self, learning_rate=0.01, n_iters=1000):
        self.learning_rate = learning_rate
        self.n_iters = n_iters
        self.weight = 0.0
        self.bias = 0.0
        self.history = []

    def fit(self, X, y):
        X = np.array(X)
        y = np.array(y)
        m = len(X)

        for _ in range(self.n_iters):
            y_pred = self.weight * X + self.bias

            error = y_pred - y
            b_grad = (1/m) * np.sum(error)
            w_grad = (1/m) * np.sum(error * X)

            self.weight -= self.learning_rate * w_grad
            self.bias -= self.learning_rate * b_grad

            mse = np.sum((y_pred-y)**2)/m
            self.history.append(mse)
        
        return self

    def predict(self, X):
        X = np.array(X)
        return self.weight * X + self.bias

    def plot_training_loss(self, X, y):
        X = np.array(X)
        y = np.array(y)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

        # 1. SSE over iterations
        ax1.plot(self.history)
        ax1.set_xlabel("iteration")
        ax1.set_ylabel("SSE")
        ax1.set_title("SSE over iterations")

        # 2. data + regression line
        ax2.scatter(X, y, label="data")
        y_line = self.predict(X)
        # sort for clean line
        order = np.argsort(X)
        ax2.plot(X[order], y_line[order], color="red", label="regression line")
        ax2.set_xlabel("X")
        ax2.set_ylabel("y")
        ax2.set_title("Regression line")
        ax2.legend()

        plt.tight_layout()
        plt.show()